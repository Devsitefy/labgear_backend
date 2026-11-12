from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EquipmentStatus = Literal["available", "issued", "maintenance", "retired"]


class EquipmentCreate(BaseModel):

    inventory_number: str = Field(
        min_length=2, max_length=50,
        description="Уникальный инвентарный номер, указанный на оборудовании.",
        examples=["LAB-011"],
    )
    name: str = Field(min_length=2, max_length=150, description="Название и модель оборудования.", examples=["Осциллограф Rigol DS1104Z"])
    category: str = Field(min_length=2, max_length=80, description="Категория для группировки и фильтрации.", examples=["Измерительное оборудование"])
    description: str | None = Field(default=None, description="Назначение, характеристики или дополнительная информация.", examples=["Четырёхканальный цифровой осциллограф."])
    location: str = Field(min_length=2, max_length=150, description="Место хранения или лаборатория.", examples=["Лаборатория 204"])

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [{
                "inventory_number": "LAB-011",
                "name": "Осциллограф Rigol DS1104Z",
                "category": "Измерительное оборудование",
                "description": "Четырёхканальный цифровой осциллограф для учебных лабораторных работ.",
                "location": "Лаборатория 204",
            }]
        },
    )


class EquipmentUpdate(BaseModel):

    name: str | None = Field(default=None, min_length=2, max_length=150, description="Новое название оборудования.", examples=["Осциллограф Rigol DS1104Z"])
    category: str | None = Field(default=None, min_length=2, max_length=80, description="Новая категория.", examples=["Измерительное оборудование"])
    description: str | None = Field(default=None, description="Новое описание оборудования.", examples=["Обновлённое описание прибора."])
    location: str | None = Field(default=None, min_length=2, max_length=150, description="Новое место хранения.", examples=["Лаборатория 205"])

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"examples": [{"location": "Лаборатория 205", "description": "Перенесён в лабораторию 205."}]},
    )


class EquipmentRead(BaseModel):

    id: int = Field(description="Уникальный идентификатор карточки.", examples=[1])
    inventory_number: str = Field(description="Инвентарный номер.", examples=["LAB-001"])
    name: str = Field(description="Название оборудования.", examples=["Осциллограф Rigol DS1054Z"])
    category: str = Field(description="Категория оборудования.", examples=["Измерительное оборудование"])
    description: str | None = Field(description="Описание и назначение оборудования.", examples=["Цифровой осциллограф для исследования электрических сигналов"])
    location: str = Field(description="Место хранения.", examples=["Лаборатория 204"])
    status: EquipmentStatus = Field(
        description="Состояние: available — доступно, issued — выдано, maintenance — на обслуживании, retired — списано.",
        examples=["available"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{
                "id": 1,
                "inventory_number": "LAB-001",
                "name": "Осциллограф Rigol DS1054Z",
                "category": "Измерительное оборудование",
                "description": "Цифровой осциллограф для исследования электрических сигналов.",
                "location": "Лаборатория 204",
                "status": "available",
            }]
        },
    )
