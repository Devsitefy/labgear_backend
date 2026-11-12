from typing import Annotated, Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_session
from src.models.user import UserOrm


bearer_scheme = HTTPBearer(auto_error=False)
DBDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    request: Request,
    db: DBDep,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> UserOrm:
    token = credentials.credentials if credentials else request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    user = await db.get(UserOrm, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


def require_roles(*roles: str) -> Callable:
    async def role_dependency(user: Annotated[UserOrm, Depends(get_current_user)]) -> UserOrm:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return user

    return role_dependency


CurrentUser = Annotated[UserOrm, Depends(get_current_user)]
StaffUser = Annotated[UserOrm, Depends(require_roles("admin", "technician"))]
AdminUser = Annotated[UserOrm, Depends(require_roles("admin"))]
