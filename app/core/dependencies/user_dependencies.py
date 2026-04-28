from typing import Union

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.enums import UserType
from app.models.user import User
from app.services.jwt_token_service import TokenService
from app.services.users.standard_user_service import UserService
from app.exceptions.auth.auth import PermissionDenied
from app.services.jwt_token_service import TokenService

from app.exceptions.users.user_exceptions import (
    UserNotFound,
)

from app.exceptions.auth.auth import (
    UserBlocked,
)
bearer = HTTPBearer(auto_error=False)


def _extract_token(credentials: Union[HTTPAuthorizationCredentials, str, None]) -> str:
    if isinstance(credentials, HTTPAuthorizationCredentials):
        scheme = credentials.scheme or ""
        token = credentials.credentials.strip()
    elif isinstance(credentials, str):
        scheme, _, token = credentials.partition(" ")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")
    return token


def _get_subject(token: str) -> str:
    payload = TokenService().decode_token(token)
    if not payload or "sub" not in payload or payload.get("token_kind") != "user":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload["sub"]



async def get_current_user(
    credentials: Union[HTTPAuthorizationCredentials, str, None] = Security(bearer),
    db: AsyncSession = Depends(get_session),
) -> User:
    token = _extract_token(credentials)
    username = _get_subject(token)

    user = await UserService(db).get_by_username(username)
    if not user:
        raise UserNotFound()
    if user.blocked:
        raise UserBlocked()
    return user







def require_user_type(*allowed_types: UserType):
    """
    Factory that returns a FastAPI dependency enforcing one or more UserType values.

    Usage:
        dependencies=[Depends(require_user_type(UserType.ADMIN))]
        dependencies=[Depends(require_user_type(UserType.ADMIN, UserType.STANDARD))]
    """
    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access restricted to: {[t.value for t in allowed_types]}",
            )
        return current_user

    return _guard



get_current_standard_user = require_user_type(UserType.STANDARD)
get_current_admin_user = require_user_type(UserType.ADMIN)
get_current_any_user = require_user_type(UserType.STANDARD, UserType.ADMIN)


def require_permission(permission: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        credentials: HTTPAuthorizationCredentials = Security(bearer),
    ) -> User:

        token = _extract_token(credentials)

        payload = TokenService().decode_token(token)  


        
        user_permissions = [
            p.strip().lower() for p in payload.get("permissions", [])
        ]

        if permission.lower() not in user_permissions:
            raise PermissionDenied()

        return current_user

    return dependency