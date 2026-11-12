from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):

    message: str = Field(description="Результат выполненной операции.", examples=["Вы вышли из системы"])

    model_config = ConfigDict(json_schema_extra={"examples": [{"message": "Вы вышли из системы"}]})


class HealthResponse(BaseModel):

    status: str = Field(description="Состояние сервиса.", examples=["ok"])
    service: str = Field(description="Внутреннее имя сервиса.", examples=["labgear-api"])

    model_config = ConfigDict(json_schema_extra={"examples": [{"status": "ok", "service": "labgear-api"}]})
