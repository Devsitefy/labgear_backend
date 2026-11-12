from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ReservationStatus = Literal[
    "pending", "approved", "rejected", "issued", "returned", "cancelled"
]


class ReservationCreate(BaseModel):

    equipment_id: int = Field(gt=0, description="Идентификатор оборудования из каталога.", examples=[1])
    starts_at: datetime = Field(
        description="Дата и время начала бронирования в ISO 8601. Обязательно укажите часовой пояс.",
        examples=["2026-11-16T10:00:00+03:00"],
    )
    ends_at: datetime = Field(
        description="Дата и время окончания бронирования. Должно быть позже начала.",
        examples=["2026-11-16T12:00:00+03:00"],
    )
    purpose: str = Field(
        min_length=5, max_length=2000,
        description="Цель использования оборудования: дисциплина, лабораторная работа или проект.",
        examples=["Выполнение лабораторной работы по исследованию электрических сигналов"],
    )

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{
                "equipment_id": 1,
                "starts_at": "2026-11-16T10:00:00+03:00",
                "ends_at": "2026-11-16T12:00:00+03:00",
                "purpose": "Выполнение лабораторной работы по исследованию электрических сигналов",
            }]
        },
    )

    @model_validator(mode="after")
    def validate_period(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Даты должны содержать часовой пояс")
        if self.ends_at <= self.starts_at:
            raise ValueError("Дата окончания должна быть позже даты начала")
        return self


class ReservationRead(BaseModel):

    id: int = Field(description="Уникальный номер заявки.", examples=[1])
    equipment_id: int = Field(description="Идентификатор забронированного оборудования.", examples=[1])
    user_id: int = Field(description="Идентификатор пользователя, создавшего заявку.", examples=[3])
    starts_at: datetime = Field(description="Начало периода бронирования.", examples=["2026-11-16T10:00:00+03:00"])
    ends_at: datetime = Field(description="Окончание периода бронирования.", examples=["2026-11-16T12:00:00+03:00"])
    purpose: str = Field(description="Цель использования оборудования.", examples=["Выполнение лабораторной работы"])
    status: ReservationStatus = Field(
        description="Статус: pending — ожидает решения; approved — подтверждено; rejected — отклонено; issued — выдано; returned — возвращено; cancelled — отменено.",
        examples=["pending"],
    )
    created_at: datetime = Field(description="Дата и время создания заявки.", examples=["2026-11-12T09:30:00+03:00"])
    approved_by: int | None = Field(description="Идентификатор сотрудника, подтвердившего заявку. Пусто, если заявка не подтверждена.", examples=[2])
    approved_at: datetime | None = Field(description="Время подтверждения заявки.", examples=["2026-11-12T10:00:00+03:00"])
    issued_at: datetime | None = Field(description="Время фактической выдачи оборудования.", examples=["2026-11-16T10:00:00+03:00"])
    returned_at: datetime | None = Field(description="Время возврата оборудования.", examples=["2026-11-16T12:00:00+03:00"])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "equipment_id": 1,
                "user_id": 3,
                "starts_at": "2026-11-16T10:00:00+03:00",
                "ends_at": "2026-11-16T12:00:00+03:00",
                "purpose": "Выполнение лабораторной работы",
                "status": "pending",
                "created_at": "2026-11-12T09:30:00+03:00",
                "approved_by": None,
                "approved_at": None,
                "issued_at": None,
                "returned_at": None,
            }]
        },
    )
