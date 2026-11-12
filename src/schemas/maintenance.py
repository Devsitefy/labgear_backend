from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceCreate(BaseModel):

    equipment_id: int = Field(gt=0, description="Идентификатор оборудования, в котором обнаружена проблема.", examples=[1])
    description: str = Field(
        min_length=5,
        max_length=2000,
        description="Подробно опишите неисправность и обстоятельства её обнаружения.",
        examples=["После включения осциллографа не отображается сигнал на экране, требуется диагностика подключения."],
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{
                "equipment_id": 1,
                "description": "После включения осциллографа не отображается сигнал на экране, требуется диагностика подключения.",
            }]
        },
    )


class MaintenanceRead(BaseModel):

    id: int = Field(description="Уникальный номер заявки на обслуживание.", examples=[1])
    equipment_id: int = Field(description="Идентификатор неисправного оборудования.", examples=[6])
    reported_by: int = Field(description="Идентификатор пользователя, сообщившего о проблеме.", examples=[4])
    description: str = Field(description="Описание обнаруженной неисправности.", examples=["Требуется калибровка оси X."])
    status: Literal["open", "in_progress", "resolved"] = Field(
        description="Состояние: open — новая заявка, in_progress — в работе, resolved — проблема устранена.",
        examples=["open"],
    )
    created_at: datetime = Field(description="Дата и время регистрации неисправности.", examples=["2026-11-12T09:30:00+03:00"])
    resolved_by: int | None = Field(description="Идентификатор сотрудника, закрывшего заявку.", examples=[2])
    resolved_at: datetime | None = Field(description="Дата и время закрытия заявки.", examples=["2026-11-13T15:00:00+03:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "equipment_id": 6,
                "reported_by": 4,
                "description": "Требуется калибровка оси X после перемещения принтера.",
                "status": "open",
                "created_at": "2026-11-12T09:30:00+03:00",
                "resolved_by": None,
                "resolved_at": None,
            }]
        },
    )
