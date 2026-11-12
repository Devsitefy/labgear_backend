from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Path, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import DBDep, StaffUser
from src.api.openapi import CONFLICT, NOT_FOUND_EQUIPMENT, STAFF_ERRORS, VALIDATION
from src.models.equipment import EquipmentOrm
from src.models.maintenance import MaintenanceRecordOrm
from src.models.reservation import ReservationOrm
from src.schemas.equipment import EquipmentCreate, EquipmentRead, EquipmentUpdate


router = APIRouter(prefix="/equipment", tags=["Оборудование"])
EquipmentStatusQuery = Literal["available", "issued", "maintenance", "retired"]


@router.get(
    "",
    response_model=list[EquipmentRead],
    summary="Получить каталог оборудования",
    description=(
        "Возвращает список оборудования с возможностью поиска и фильтрации. По умолчанию списанные "
        "позиции (`retired`) не показываются. **Авторизация не требуется** — каталог доступен всем посетителям."
    ),
    response_description="Список карточек оборудования. Если совпадений нет, возвращается пустой список.",
    responses=VALIDATION,
)
async def list_equipment(
    db: DBDep,
    search: str | None = Query(
        default=None, min_length=1, max_length=100,
        description="Поиск по названию оборудования или инвентарному номеру.",
        openapi_examples={"по названию": {"summary": "Найти осциллограф", "value": "осциллограф"}, "по инвентарному номеру": {"summary": "Найти по номеру", "value": "LAB-001"}},
    ),
    category: str | None = Query(
        default=None, max_length=80,
        description="Фильтр по категории оборудования.",
        openapi_examples={"пример": {"summary": "Измерительное оборудование", "value": "Измерительное оборудование"}},
    ),
    equipment_status: Annotated[
        EquipmentStatusQuery | None,
        Query(
            alias="status",
            description="Фильтр по состоянию: available — доступно, issued — выдано, maintenance — на обслуживании, retired — списано.",
            openapi_examples={"доступно": {"summary": "Показать доступное оборудование", "value": "available"}},
        ),
    ] = None,
    skip: int = Query(default=0, ge=0, description="Сколько первых записей пропустить. Используется для постраничной загрузки.", examples=[0]),
    limit: int = Query(default=50, ge=1, le=200, description="Максимальное количество записей в ответе (от 1 до 200).", examples=[20]),
):
    query = select(EquipmentOrm)
    if search:
        query = query.where(EquipmentOrm.name.ilike(f"%{search}%") | EquipmentOrm.inventory_number.ilike(f"%{search}%"))
    if category:
        query = query.where(EquipmentOrm.category.ilike(f"%{category}%"))
    if equipment_status:
        query = query.where(EquipmentOrm.status == equipment_status)
    else:
        query = query.where(EquipmentOrm.status != "retired")
    result = await db.scalars(query.order_by(EquipmentOrm.name).offset(skip).limit(limit))
    return result.all()


@router.get(
    "/{equipment_id}",
    response_model=EquipmentRead,
    summary="Получить карточку оборудования",
    description="Возвращает подробную информацию об одной позиции каталога по её идентификатору. Авторизация не требуется.",
    response_description="Карточка выбранного оборудования.",
    responses={**NOT_FOUND_EQUIPMENT, **VALIDATION},
)
async def get_equipment(
    equipment_id: Annotated[int, Path(gt=0, description="Идентификатор оборудования из каталога.", examples=[1])],
    db: DBDep,
):
    equipment = await db.get(EquipmentOrm, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    return equipment


@router.post(
    "",
    response_model=EquipmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить оборудование",
    description="Создаёт новую карточку в каталоге. Инвентарный номер должен быть уникальным. **Доступно администратору и технику.** Новая позиция получает статус `available`.",
    response_description="Карточка успешно созданного оборудования.",
    responses={**STAFF_ERRORS, **CONFLICT},
)
async def create_equipment(data: EquipmentCreate, db: DBDep, _: StaffUser):
    equipment = EquipmentOrm(**data.model_dump())
    db.add(equipment)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Инвентарный номер уже используется")
    await db.refresh(equipment)
    return equipment


@router.patch(
    "/{equipment_id}",
    response_model=EquipmentRead,
    summary="Изменить карточку оборудования",
    description="Обновляет только переданные поля карточки. Нельзя отправлять пустой объект. **Доступно администратору и технику.** Статус оборудования этим методом не меняется.",
    response_description="Карточка с обновлёнными данными.",
    responses={**STAFF_ERRORS, **NOT_FOUND_EQUIPMENT, 400: {"description": "Не переданы поля для изменения.", "content": {"application/json": {"example": {"detail": "Не переданы поля для изменения"}}}}},
)
async def update_equipment(
    equipment_id: Annotated[int, Path(gt=0, description="Идентификатор редактируемой позиции.", examples=[1])],
    data: EquipmentUpdate,
    db: DBDep,
    _: StaffUser,
):
    equipment = await db.get(EquipmentOrm, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    changes = data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="Не переданы поля для изменения")
    for field, value in changes.items():
        setattr(equipment, field, value)
    await db.commit()
    await db.refresh(equipment)
    return equipment


@router.delete(
    "/{equipment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Списать оборудование",
    description=(
        "Не удаляет запись физически, а переводит оборудование в статус `retired`. "
        "Списание запрещено, если есть активное бронирование, незавершённая выдача или открытая заявка на обслуживание. "
        "**Доступно администратору и технику.**"
    ),
    response_description="Оборудование списано. Тело ответа отсутствует.",
    responses={**STAFF_ERRORS, **NOT_FOUND_EQUIPMENT, **CONFLICT},
)
async def retire_equipment(
    equipment_id: Annotated[int, Path(gt=0, description="Идентификатор оборудования для списания.", examples=[1])],
    db: DBDep,
    _: StaffUser,
):
    equipment = await db.get(EquipmentOrm, equipment_id, with_for_update=True)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Оборудование не найдено")
    if equipment.status == "retired":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    active_reservation = await db.scalar(
        select(ReservationOrm.id).where(
            ReservationOrm.equipment_id == equipment_id,
            ReservationOrm.status.in_(["pending", "approved", "issued"]),
        ).limit(1)
    )
    if active_reservation is not None:
        raise HTTPException(status_code=409, detail="Нельзя списать оборудование с активными бронированиями или выдачей")

    unresolved_issue = await db.scalar(
        select(MaintenanceRecordOrm.id).where(
            MaintenanceRecordOrm.equipment_id == equipment_id,
            MaintenanceRecordOrm.status.in_(["open", "in_progress"]),
        ).limit(1)
    )
    if unresolved_issue is not None:
        raise HTTPException(status_code=409, detail="Сначала закройте незавершённую заявку на обслуживание")

    equipment.status = "retired"
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
