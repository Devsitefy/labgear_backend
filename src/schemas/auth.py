from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):

    email: EmailStr = Field(description="Рабочий email пользователя. Должен быть уникальным.", examples=["student3@labgear.com"])
    password: str = Field(
        min_length=8,
        max_length=72,
        description="Пароль длиной от 8 до 72 символов.",
        examples=["Student123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"email": "student3@labgear.com", "password": "Student123!"}]}
    )


class LoginRequest(BaseModel):

    email: EmailStr = Field(description="Email, указанный при регистрации.", examples=["student@labgear.com"])
    password: str = Field(description="Пароль учётной записи.", examples=["Student123!"])

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"email": "student@labgear.com", "password": "Student123!"}]}
    )


class UserRead(BaseModel):

    id: int = Field(description="Уникальный идентификатор пользователя.", examples=[3])
    email: EmailStr = Field(description="Email пользователя.", examples=["student@labgear.com"])
    role: Literal["student", "technician", "admin"] = Field(
        description="Роль: student — студент, technician — техник, admin — администратор.",
        examples=["student"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [{"id": 3, "email": "student@labgear.com", "role": "student"}]
        },
    )


class TokenResponse(BaseModel):

    access_token: str = Field(
        description="JWT-токен. Скопируйте его в Swagger через кнопку Authorize.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo.signature"],
    )
    token_type: str = Field(default="bearer", description="Тип токена авторизации.", examples=["bearer"])
    user: UserRead = Field(description="Профиль пользователя, выполнившего вход.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo.signature",
                    "token_type": "bearer",
                    "user": {"id": 3, "email": "student@labgear.com", "role": "student"},
                }
            ]
        }
    )


class UserRoleUpdate(BaseModel):

    role: Literal["student", "technician", "admin"] = Field(
        description="Назначаемая роль: student — студент, technician — техник, admin — администратор.",
        examples=["technician"],
    )

    model_config = ConfigDict(json_schema_extra={"examples": [{"role": "technician"}]})
