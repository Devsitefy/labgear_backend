from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.api.dependencies import AdminUser, CurrentUser, DBDep
from src.api.openapi import AUTH_ERRORS, STAFF_ERRORS
from src.config import settings
from src.models.user import UserOrm
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserRead, UserRoleUpdate
from src.schemas.common import MessageResponse
from src.services.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Авторизация"])
users_router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Зарегистрировать пользователя",
    description=(
        "Создаёт новую учётную запись. **Роль автоматически назначается как `student`** — "
        "пользователь не может самостоятельно зарегистрироваться техником или администратором. "
        "Email должен быть уникальным, пароль — не короче 8 символов."
    ),
    response_description="Учётная запись создана. Возвращается профиль без пароля.",
    responses={
        409: {"description": "Пользователь с таким email уже зарегистрирован.", "content": {"application/json": {"example": {"detail": "Пользователь с таким email уже зарегистрирован"}}}},
        422: AUTH_ERRORS[422],
    },
)
async def register(data: RegisterRequest, db: DBDep):
    user = UserOrm(email=data.email, hashed_password=hash_password(data.password), role="student")
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже зарегистрирован")
    await db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Войти в систему",
    description=(
        "Проверяет email и пароль. При успешном входе возвращает JWT в поле `access_token` "
        "и устанавливает HttpOnly cookie. Для авторизации запросов из Swagger нажмите **Authorize** "
        "и вставьте значение `access_token` без префикса `Bearer`."
    ),
    response_description="Вход выполнен. Возвращены токен доступа и профиль пользователя.",
    responses={
        401: {"description": "Неверный email или пароль.", "content": {"application/json": {"example": {"detail": "Неверный email или пароль"}}}},
        422: AUTH_ERRORS[422],
    },
)
async def login(data: LoginRequest, response: Response, db: DBDep):
    user = await db.scalar(select(UserOrm).where(UserOrm.email == data.email))
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    token = create_access_token(user.id)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.MODE == "PROD",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {"access_token": token, "user": user}


@router.get(
    "/me",
    response_model=UserRead,
    summary="Получить мой профиль",
    description="Возвращает профиль пользователя, чей токен передан в запросе. Пароль и его хеш никогда не возвращаются.",
    response_description="Профиль текущего пользователя.",
    responses=AUTH_ERRORS,
)
async def get_me(user: CurrentUser):
    return user


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Выйти из системы",
    description=(
        "Удаляет cookie `access_token` на стороне клиента. Если токен передавался через заголовок Bearer, "
        "клиентскому приложению также следует удалить его из своего хранилища."
    ),
    response_description="Cookie авторизации удалена.",
    responses={200: {"content": {"application/json": {"example": {"message": "Вы вышли из системы"}}}}},
)
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Вы вышли из системы"}


@users_router.get(
    "",
    response_model=list[UserRead],
    summary="Получить список пользователей",
    description="Возвращает все учётные записи, отсортированные по идентификатору. **Доступно только администратору.**",
    response_description="Список пользователей без паролей и служебных секретов.",
    responses=STAFF_ERRORS,
)
async def get_users(db: DBDep, _: AdminUser):
    result = await db.scalars(select(UserOrm).order_by(UserOrm.id))
    return result.all()


@users_router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    summary="Изменить роль пользователя",
    description=(
        "Назначает пользователю одну из ролей: `student`, `technician` или `admin`. "
        "Операция доступна только администратору. Используйте её для предоставления сотруднику "
        "прав техника или для изменения роли пользователя."
    ),
    response_description="Профиль пользователя с обновлённой ролью.",
    responses={**STAFF_ERRORS, 404: {"description": "Пользователь не найден.", "content": {"application/json": {"example": {"detail": "Пользователь не найден"}}}}},
)
async def change_user_role(
    user_id: Annotated[int, Path(gt=0, description="Идентификатор пользователя, которому нужно изменить роль.", examples=[3])],
    data: UserRoleUpdate,
    db: DBDep,
    _: AdminUser,
):
    user = await db.get(UserOrm, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.role = data.role
    await db.commit()
    await db.refresh(user)
    return user
