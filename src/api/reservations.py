from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBDep, StaffUser
from src.api.openapi import CONFLICT, NOT_FOUND_EQUIPMENT, NOT_FOUND_RESERVATION, STAFF_ERRORS, UNAUTHORIZED, VALIDATION
from src.models.equipment import EquipmentOrm
from src.models.maintenance import MaintenanceRecordOrm
from src.models.reservation import ReservationOrm
from src.schemas.reservation import ReservationCreate, ReservationRead


router = APIRouter(prefix="/reservations", tags=["Бронирования"])
ACTIVE_STATUSES = ("pending", "approved", "issued")


async def get_reservation_for_update(db: DBDep, reservation_id: int) -> ReservationOrm:
    reservation = await db.scalar(
        select(ReservationOrm).where(ReservationOrm.id == reservation_id).with_for_update()
    )
    if reservation is None:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return reservation


@router.post(
    "",
    response_model=ReservationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать заявку на бронирование",
    description=(
        "Создаёт заявку на использование оборудования в выбранный период. **Доступно всем авторизованным пользователям, включая студентов.** "
        "Новая заявка получает статус `pending` и ожидает подтверждения техника или администратора. "
        "Система проверяет доступность оборудования и не допускает пересечения с другими активными бронированиями. "
        "Дата и время должны содержать часовой пояс."
    ),
    response_description="Созданная заявка со статусом `pending`.",
    responses={**UNAUTHORIZED, **NOT_FOUND_EQUIPMENT, **CONFLICT, **VALIDATION},
)
async def create_reservation(data: ReservationCreate, db: DBDep, user: CurrentUser):
    equipment = await db.scalar(
        select(EquipmentOrm).where(EquipmentOrm.id == data.equipment_id).with_for_update()
    )
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    if equipment.status in ("maintenance", "retired"):
        raise HTTPException(status_code=409, detail="Оборудование недоступно для бронирования")

    overlap = await db.scalar(
        select(ReservationOrm.id).where(
            ReservationOrm.equipment_id == data.equipment_id,
            ReservationOrm.status.in_(ACTIVE_STATUSES),
            ReservationOrm.starts_at < data.ends_at,
            ReservationOrm.ends_at > data.starts_at,
        ).limit(1)
    )
    if overlap is not None:
        raise HTTPException(status_code=409, detail="На выбранный период оборудование уже забронировано")

    reservation = ReservationOrm(
        equipment_id=data.equipment_id,
        user_id=user.id,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        purpose=data.purpose,
        status="pending",
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.get(
    "/me",
    response_model=list[ReservationRead],
    summary="Получить мои бронирования",
    description="Возвращает только заявки текущего пользователя, от новых к старым. Доступно студенту, технику и администратору.",
    response_description="Список собственных заявок. Если заявок нет, возвращается пустой список.",
    responses={**UNAUTHORIZED, **VALIDATION},
)
async def list_my_reservations(db: DBDep, user: CurrentUser):
    result = await db.scalars(
        select(ReservationOrm)
        .where(ReservationOrm.user_id == user.id)
        .order_by(ReservationOrm.created_at.desc())
    )
    return result.all()


@router.get(
    "",
    response_model=list[ReservationRead],
    summary="Получить все бронирования",
    description="Возвращает заявки всех пользователей. **Доступно только администратору и технику.** Для просмотра собственных заявок используйте `GET /reservations/me`.",
    response_description="Полный список заявок, отсортированный от новых к старым.",
    responses=STAFF_ERRORS,
)
async def list_all_reservations(db: DBDep, _: StaffUser):
    result = await db.scalars(select(ReservationOrm).order_by(ReservationOrm.created_at.desc()))
    return result.all()


@router.post(
    "/{reservation_id}/approve",
    response_model=ReservationRead,
    summary="Подтвердить бронирование",
    description="Переводит новую заявку (`pending`) в статус `approved` и сохраняет сотрудника, который её подтвердил. **Доступно администратору и технику.**",
    response_description="Заявка со статусом `approved`.",
    responses={**STAFF_ERRORS, **NOT_FOUND_RESERVATION, **CONFLICT},
)
async def approve_reservation(
    reservation_id: Annotated[int, Path(gt=0, description="Номер заявки на бронирование.", examples=[1])],
    db: DBDep,
    staff: StaffUser,
):
    reservation = await get_reservation_for_update(db, reservation_id)
    if reservation.status != "pending":
        raise HTTPException(status_code=409, detail="Подтвердить можно только новую заявку")
    equipment = await db.get(EquipmentOrm, reservation.equipment_id)
    if equipment is None or equipment.status in ("maintenance", "retired"):
        raise HTTPException(status_code=409, detail="Оборудование сейчас недоступно")
    reservation.status = "approved"
    reservation.approved_by = staff.id
    reservation.approved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.post(
    "/{reservation_id}/reject",
    response_model=ReservationRead,
    summary="Отклонить бронирование",
    description="Переводит новую заявку (`pending`) в статус `rejected`. Повторно обработать отклонённую заявку нельзя — пользователь может создать новую. **Доступно администратору и технику.**",
    response_description="Заявка со статусом `rejected`.",
    responses={**STAFF_ERRORS, **NOT_FOUND_RESERVATION, **CONFLICT},
)
async def reject_reservation(
    reservation_id: Annotated[int, Path(gt=0, description="Номер заявки на бронирование.", examples=[1])],
    db: DBDep,
    _: StaffUser,
):
    reservation = await get_reservation_for_update(db, reservation_id)
    if reservation.status != "pending":
        raise HTTPException(status_code=409, detail="Отклонить можно только новую заявку")
    reservation.status = "rejected"
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.post(
    "/{reservation_id}/issue",
    response_model=ReservationRead,
    summary="Выдать оборудование пользователю",
    description=(
        "Фиксирует фактическую выдачу. Выдать можно только подтверждённую заявку (`approved`), "
        "если текущий момент попадает в период бронирования и оборудование не выдано, не находится на обслуживании и не списано. "
        "Статус заявки и оборудования меняется на `issued`. **Доступно администратору и технику.**"
    ),
    response_description="Заявка со статусом `issued` и заполненным временем выдачи.",
    responses={**STAFF_ERRORS, **NOT_FOUND_RESERVATION, **CONFLICT},
)
async def issue_equipment(
    reservation_id: Annotated[int, Path(gt=0, description="Номер подтверждённой заявки.", examples=[2])],
    db: DBDep,
    _: StaffUser,
):
    reservation = await get_reservation_for_update(db, reservation_id)
    if reservation.status != "approved":
        raise HTTPException(status_code=409, detail="Выдать можно только подтверждённое бронирование")

    now = datetime.now(timezone.utc)
    if reservation.starts_at > now:
        raise HTTPException(status_code=409, detail="Период бронирования ещё не начался")
    if reservation.ends_at <= now:
        raise HTTPException(status_code=409, detail="Срок бронирования уже закончился")

    equipment = await db.get(EquipmentOrm, reservation.equipment_id, with_for_update=True)
    if equipment is None or equipment.status in ("maintenance", "retired", "issued"):
        raise HTTPException(status_code=409, detail="Оборудование нельзя выдать в текущем состоянии")

    equipment.status = "issued"
    reservation.status = "issued"
    reservation.issued_at = now
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.post(
    "/{reservation_id}/return",
    response_model=ReservationRead,
    summary="Принять оборудование обратно",
    description="Фиксирует возврат ранее выданного оборудования. Заявка получает статус `returned`, а оборудование становится доступным, если по нему нет незакрытых заявок на обслуживание. **Доступно администратору и технику.**",
    response_description="Заявка со статусом `returned` и заполненным временем возврата.",
    responses={**STAFF_ERRORS, **NOT_FOUND_RESERVATION, **CONFLICT},
)
async def return_equipment(
    reservation_id: Annotated[int, Path(gt=0, description="Номер заявки, по которой оборудование было выдано.", examples=[2])],
    db: DBDep,
    _: StaffUser,
):
    reservation = await get_reservation_for_update(db, reservation_id)
    if reservation.status != "issued":
        raise HTTPException(status_code=409, detail="Вернуть можно только выданное оборудование")

    equipment = await db.get(EquipmentOrm, reservation.equipment_id, with_for_update=True)
    reservation.status = "returned"
    reservation.returned_at = datetime.now(timezone.utc)

    open_maintenance = await db.scalar(
        select(MaintenanceRecordOrm.id).where(
            MaintenanceRecordOrm.equipment_id == reservation.equipment_id,
            MaintenanceRecordOrm.status.in_(["open", "in_progress"]),
        ).limit(1)
    )
    if equipment is not None and equipment.status != "retired":
        equipment.status = "maintenance" if open_maintenance is not None else "available"

    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationRead,
    summary="Отменить бронирование",
    description="Отменяет заявку в статусе `pending` или `approved`. Студент может отменить только собственную заявку; техник и администратор — любую. Выданное оборудование через этот метод отменить нельзя.",
    response_description="Заявка со статусом `cancelled`.",
    responses={**UNAUTHORIZED, **NOT_FOUND_RESERVATION, 403: {"description": "Попытка отменить чужую заявку.", "content": {"application/json": {"example": {"detail": "Нельзя отменить чужое бронирование"}}}}, **CONFLICT},
)
async def cancel_reservation(
    reservation_id: Annotated[int, Path(gt=0, description="Номер заявки, которую требуется отменить.", examples=[1])],
    db: DBDep,
    user: CurrentUser,
):
    reservation = await get_reservation_for_update(db, reservation_id)
    is_staff = user.role in ("admin", "technician")
    if reservation.user_id != user.id and not is_staff:
        raise HTTPException(status_code=403, detail="Нельзя отменить чужое бронирование")
    if reservation.status not in ("pending", "approved"):
        raise HTTPException(status_code=409, detail="Отменить можно только новую или подтверждённую заявку")
    reservation.status = "cancelled"
    await db.commit()
    await db.refresh(reservation)
    return reservation
