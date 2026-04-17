from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserType
from app.core.security.verify_password import verify_password
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.jwt_token_service import TokenService
from app.services.users.user_service import UserService

from app.exceptions.auth.auth import (
    InvalidCredentials,
    UserBlocked,
    AccountNotActivated,
)

class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def login(
        self,
        data: LoginRequest,
        allowed_type: Optional[UserType] = None
    ) -> TokenResponse:

        user = await UserService(self.session).get_by_username(data.username)

        if not user or not verify_password(data.password, user.password):
            raise InvalidCredentials()

        if allowed_type is not None and user.type != allowed_type:
            raise InvalidCredentials()

        if user.blocked:
            raise UserBlocked()

        if not user.activated:
            raise AccountNotActivated()

        token = TokenService().create_access_token({
            "sub": user.username,
            "user_id": str(user.id),
            "type": user.type.value,
            "token_kind": "user",
        })

        return TokenResponse(access_token=token)