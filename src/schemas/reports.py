from pydantic import BaseModel, ConfigDict, Field


class SummaryReport(BaseModel):

    equipment_total: int = Field(description="Общее количество единиц оборудования, включая списанное.", examples=[10])
    available: int = Field(description="Количество доступных единиц оборудования.", examples=[7])
    issued: int = Field(description="Количество единиц, выданных пользователям.", examples=[1])
    maintenance: int = Field(description="Количество единиц на техническом обслуживании.", examples=[1])
    retired: int = Field(description="Количество списанных единиц.", examples=[1])
    active_reservations: int = Field(description="Количество активных заявок: ожидающих, подтверждённых или выданных.", examples=[3])
    pending_reservations: int = Field(description="Количество заявок, ожидающих решения сотрудника.", examples=[1])
    overdue_returns: int = Field(description="Количество выданных единиц, срок возврата которых уже прошёл.", examples=[0])
    open_maintenance: int = Field(description="Количество заявок на обслуживание, которые ещё не закрыты.", examples=[1])

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "equipment_total": 10,
        "available": 7,
        "issued": 1,
        "maintenance": 1,
        "retired": 1,
        "active_reservations": 3,
        "pending_reservations": 1,
        "overdue_returns": 0,
        "open_maintenance": 1,
    }]})


class EquipmentCategoryCount(BaseModel):

    category: str = Field(description="Название категории оборудования.", examples=["Измерительное оборудование"])
    count: int = Field(description="Количество единиц в категории, кроме списанных.", examples=[3])

    model_config = ConfigDict(json_schema_extra={"examples": [{"category": "Измерительное оборудование", "count": 3}]})
