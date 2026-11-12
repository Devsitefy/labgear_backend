from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBDep, StaffUser
from src.api.openapi import CONFLICT, NOT_FOUND_EQUIPMENT, NOT_FOUND_MAINTENANCE, STAFF_ERRORS, UNAUTHORIZED, VALIDATION
from src.models.equipment import EquipmentOrm
from src.models.maintenance import MaintenanceRecordOrm
from src.models.reservation import ReservationOrm
from src.schemas.maintenance import MaintenanceCreate, MaintenanceRead


router = APIRouter(prefix="/maintenance", tags=["Техническое обслуживание"])


@router.post(
    "",
    response_model=MaintenanceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Сообщить о неисправности",
    description=(
        "Регистрирует проблему с оборудованием и автоматически переводит его в статус `maintenance`, "
        "чтобы его нельзя было забронировать до устранения неисправности. Сообщить о проблеме может "
        "любой авторизованный пользователь. Списанное оборудование нельзя отправить на обслуживание."
    ),
    response_description="Созданная заявка со статусом `open`.",
    responses={**UNAUTHORIZED, **NOT_FOUND_EQUIPMENT, **CONFLICT, **VALIDATION},
)
async def report_problem(data: MaintenanceCreate, db: DBDep, user: CurrentUser):
    equipment = await db.scalar(
        select(EquipmentOrm).where(EquipmentOrm.id == data.equipment_id).with_for_update()
    )
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    if equipment.status == "retired":
        raise HTTPException(status_code=409, detail="Списанное оборудование нельзя отправить на обслуживание")

    record = MaintenanceRecordOrm(
        equipment_id=equipment.id,
        reported_by=user.id,
        description=data.description,
        status="open",
    )
    equipment.status = "maintenance"
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get(
    "/me",
    response_model=list[MaintenanceRead],
    summary="Получить мои сообщения о неисправностях",
    description="Возвращает заявки на обслуживание, созданные текущим пользователем. Доступно всем авторизованным пользователям.",
    response_description="Список собственных заявок на обслуживание.",
    responses={**UNAUTHORIZED, **VALIDATION},
)
async def list_my_reports(db: DBDep, user: CurrentUser):
    result = await db.scalars(
        select(MaintenanceRecordOrm)
        .where(MaintenanceRecordOrm.reported_by == user.id)
        .order_by(MaintenanceRecordOrm.created_at.desc())
    )
    return result.all()


@router.get(
    "",
    response_model=list[MaintenanceRead],
    summary="Получить все заявки на обслуживание",
    description="Возвращает заявки всех пользователей, отсортированные от новых к старым. **Доступно администратору и технику.**",
    response_description="Полный список заявок на техническое обслуживание.",
    responses=STAFF_ERRORS,
)
async def list_all_reports(db: DBDep, _: StaffUser):
    result = await db.scalars(
        select(MaintenanceRecordOrm).order_by(MaintenanceRecordOrm.created_at.desc())
    )
    return result.all()


@router.post(
    "/{record_id}/start",
    response_model=MaintenanceRead,
    summary="Взять заявку в работу",
    description="Меняет статус открытой заявки с `open` на `in_progress`. Повторно взять уже выполняемую или закрытую заявку нельзя. **Доступно администратору и технику.**",
    response_description="Заявка со статусом `in_progress`.",
    responses={**STAFF_ERRORS, **NOT_FOUND_MAINTENANCE, **CONFLICT},
)
async def start_maintenance(
    record_id: Annotated[int, Path(gt=0, description="Номер заявки на обслуживание.", examples=[1])],
    db: DBDep,
    _: StaffUser,
):
    record = await db.get(MaintenanceRecordOrm, record_id, with_for_update=True)
    if record is None:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    if record.status != "open":
        raise HTTPException(status_code=409, detail="В работу можно взять только открытую заявку")
    record.status = "in_progress"
    await db.commit()
    await db.refresh(record)
    return record


@router.post(
    "/{record_id}/resolve",
    response_model=MaintenanceRead,
    summary="Закрыть заявку на обслуживание",
    description=(
        "Отмечает неисправность как устранённую, сохраняет сотрудника и время закрытия. "
        "Если по оборудованию не осталось других открытых заявок и оно не списано, "
        "его статус возвращается к `available` (либо `issued`, если оно ещё выдано). "
        "**Доступно администратору и технику.**"
    ),
    response_description="Заявка со статусом `resolved`.",
    responses={**STAFF_ERRORS, **NOT_FOUND_MAINTENANCE, **CONFLICT},
)
async def resolve_maintenance(
    record_id: Annotated[int, Path(gt=0, description="Номер заявки, которую требуется закрыть.", examples=[1])],
    db: DBDep,
    staff: StaffUser,
):
    record = await db.get(MaintenanceRecordOrm, record_id, with_for_update=True)
    if record is None:
        raise HTTPException(status_code=404, detail="Заявка на обслуживание не найдена")
    if record.status == "resolved":
        raise HTTPException(status_code=409, detail="Заявка уже закрыта")

    record.status = "resolved"
    record.resolved_by = staff.id
    record.resolved_at = datetime.now(timezone.utc)

    other_open_records = await db.scalar(
        select(MaintenanceRecordOrm.id).where(
            MaintenanceRecordOrm.equipment_id == record.equipment_id,
            MaintenanceRecordOrm.id != record.id,
            MaintenanceRecordOrm.status.in_(["open", "in_progress"]),
        ).limit(1)
    )
    equipment = await db.get(EquipmentOrm, record.equipment_id, with_for_update=True)
    if equipment is not None and equipment.status != "retired" and other_open_records is None:
        active_loan = await db.scalar(
            select(ReservationOrm.id).where(
                ReservationOrm.equipment_id == record.equipment_id,
                ReservationOrm.status == "issued",
            ).limit(1)
        )
        equipment.status = "issued" if active_loan is not None else "available"

    await db.commit()
    await db.refresh(record)
    return record
