from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from src.api.auth import router as auth_router, users_router
from src.api.equipment import router as equipment_router
from src.api.maintenance import router as maintenance_router
from src.api.reports import router as reports_router
from src.api.reservations import router as reservations_router
from src.config import settings
from src.database import async_session_maker
from src.models.user import UserOrm
from src.schemas.common import HealthResponse
from src.services.security import hash_password


async def create_or_promote_initial_admin() -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return
    async with async_session_maker() as session:
        user = await session.scalar(select(UserOrm).where(UserOrm.email == settings.ADMIN_EMAIL))
        if user is None:
            user = UserOrm(
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="admin",
            )
            session.add(user)
        else:
            user.role = "admin"
        await session.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_or_promote_initial_admin()
    yield


OPENAPI_TAGS = [
    {
        "name": "Авторизация",
        "description": "Регистрация, вход, выход и получение профиля. После входа используйте access token через кнопку **Authorize** в верхней части Swagger.",
    },
    {
        "name": "Пользователи",
        "description": "Просмотр списка пользователей и управление ролями. Доступно только администратору.",
    },
    {
        "name": "Оборудование",
        "description": "Каталог лабораторного оборудования: поиск, просмотр карточек, добавление, редактирование и списание. Изменять каталог могут администратор и техник.",
    },
    {
        "name": "Бронирования",
        "description": "Создание и сопровождение заявок. Студент работает со своими заявками; администратор и техник просматривают и обрабатывают все заявки, подтверждают их, выдают и принимают оборудование.",
    },
    {
        "name": "Техническое обслуживание",
        "description": "Регистрация неисправностей и контроль ремонта. Сообщить о проблеме может любой авторизованный пользователь; менять статус заявки могут администратор и техник.",
    },
    {
        "name": "Отчёты",
        "description": "Сводные показатели по оборудованию, бронированиям и техническому обслуживанию. Доступно администратору и технику.",
    },
    {
        "name": "Служебное",
        "description": "Проверка доступности API и состояния сервиса.",
    },
]

app = FastAPI(
    title="LabGear — учёт и бронирование лабораторного оборудования",
    summary="Сервис для управления лабораторным оборудованием и заявками на его использование.",
    version="1.1.0",
    description=(
        "## О системе\n"
        "LabGear помогает вести каталог лабораторного оборудования, бронировать его, "
        "согласовывать заявки, фиксировать выдачу и возврат, регистрировать неисправности и смотреть отчёты.\n\n"
        "## Роли пользователей\n"
        "- **student (Студент)** — просмотр каталога, создание и отмена собственных бронирований, "
        "просмотр своих заявок, регистрация неисправностей.\n"
        "- **technician (Техник)** — возможности студента, управление каталогом, обработка бронирований, "
        "выдача и возврат оборудования, обработка неисправностей, просмотр отчётов.\n"
        "- **admin (Администратор)** — все возможности техника, а также управление пользователями и их ролями.\n\n"
        "## Как авторизоваться в Swagger\n"
        "1. Выполните `POST /auth/login`, передав email и пароль.\n"
        "2. Скопируйте значение `access_token` из ответа.\n"
        "3. Нажмите **Authorize** и вставьте токен без слова `Bearer`.\n"
        "4. После этого Swagger будет автоматически передавать токен в защищённые запросы.\n\n"
        "## Статусы\n"
        "Оборудование: `available` — доступно, `issued` — выдано, `maintenance` — на обслуживании, `retired` — списано.\n\n"
        "Бронирование: `pending` — ожидает решения, `approved` — подтверждено, `rejected` — отклонено, "
        "`issued` — оборудование выдано, `returned` — возвращено, `cancelled` — отменено.\n\n"
        "Техническое обслуживание: `open` — новая заявка, `in_progress` — в работе, `resolved` — проблема устранена.\n\n"
        "Все даты передаются в ISO 8601 вместе с часовым поясом, например `2026-11-16T10:00:00+03:00`."
    ),
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(equipment_router)
app.include_router(reservations_router)
app.include_router(maintenance_router)
app.include_router(reports_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Служебное"],
    summary="Проверить доступность API",
    description="Возвращает короткий ответ, подтверждающий, что приложение запущено и принимает запросы. Авторизация не требуется.",
    response_description="Сервис доступен.",
)
async def health_check():
    return {"status": "ok", "service": "labgear-api"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
