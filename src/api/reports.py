from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import func, select

from src.api.dependencies import DBDep, StaffUser
from src.api.openapi import STAFF_ERRORS
from src.models.equipment import EquipmentOrm
from src.models.maintenance import MaintenanceRecordOrm
from src.models.reservation import ReservationOrm
from src.schemas.reports import EquipmentCategoryCount, SummaryReport


router = APIRouter(prefix="/reports", tags=["Отчёты"])


async def count_rows(db: DBDep, model, *conditions) -> int:
    value = await db.scalar(select(func.count()).select_from(model).where(*conditions))
    return int(value or 0)


@router.get(
    "/summary",
    response_model=SummaryReport,
    summary="Получить сводную статистику",
    description=(
        "Формирует общую сводку по лаборатории: сколько оборудования всего и в каждом состоянии, "
        "сколько активных и ожидающих заявок, есть ли просроченные возвраты и незакрытые неисправности. "
        "**Доступно администратору и технику.**"
    ),
    response_description="Набор количественных показателей на момент запроса.",
    responses=STAFF_ERRORS,
)
async def get_summary(db: DBDep, _: StaffUser):
    now = datetime.now(timezone.utc)
    return {
        "equipment_total": await count_rows(db, EquipmentOrm),
        "available": await count_rows(db, EquipmentOrm, EquipmentOrm.status == "available"),
        "issued": await count_rows(db, EquipmentOrm, EquipmentOrm.status == "issued"),
        "maintenance": await count_rows(db, EquipmentOrm, EquipmentOrm.status == "maintenance"),
        "retired": await count_rows(db, EquipmentOrm, EquipmentOrm.status == "retired"),
        "active_reservations": await count_rows(
            db, ReservationOrm, ReservationOrm.status.in_(["pending", "approved", "issued"])
        ),
        "pending_reservations": await count_rows(
            db, ReservationOrm, ReservationOrm.status == "pending"
        ),
        "overdue_returns": await count_rows(
            db, ReservationOrm, ReservationOrm.status == "issued", ReservationOrm.ends_at < now
        ),
        "open_maintenance": await count_rows(
            db, MaintenanceRecordOrm, MaintenanceRecordOrm.status.in_(["open", "in_progress"])
        ),
    }


@router.get(
    "/by-category",
    response_model=list[EquipmentCategoryCount],
    summary="Посчитать оборудование по категориям",
    description="Группирует оборудование по категориям и возвращает количество единиц в каждой из них. Списанное оборудование не учитывается. **Доступно администратору и технику.**",
    response_description="Список категорий и количества оборудования в каждой категории.",
    responses=STAFF_ERRORS,
)
async def get_equipment_by_category(db: DBDep, _: StaffUser):
    result = await db.execute(
        select(EquipmentOrm.category, func.count(EquipmentOrm.id).label("count"))
        .where(EquipmentOrm.status != "retired")
        .group_by(EquipmentOrm.category)
        .order_by(EquipmentOrm.category)
    )
    return [{"category": category, "count": count} for category, count in result.all()]
