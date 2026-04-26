from typing import Optional
from uuid import UUID
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import UserType
from app.core.security.verify_password import verify_password
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    MessageResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest
)
from app.services.jwt_token_service import TokenService
from app.services.users.user_service import UserService
from app.services.mail_service import MailService

from app.exceptions.auth.auth import (
    InvalidCredentials,
    UserBlocked,
    AccountNotActivated,
    PasswordResetTokenNotFound,
    PasswordResetTokenInvalid
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def login(
        self,
        data: LoginRequest,
        allowed_type: Optional[UserType] = None
    ) -> TokenResponse:

        user = await UserService(self.session).get_by_username_or_email(data.identifier)

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

    async def forgot_password(
        self, 
        data: ForgotPasswordRequest,
        background_tasks: BackgroundTasks
        ) -> MessageResponse:
        
        user = await UserService(self.session).get_by_email(data.email)
        
        if user:
            token = TokenService().create_reset_token(
                data={
                    "sub": user.username,
                    "user_id": str(user.id),
                    "token_kind": "reset"   
                }
            )
            
            background_tasks.add_task(
                MailService().send_reset_password_email,
                user.email,
                token,
                user.type.value
            )
        
        return {"message": "Si el correo electrónico está registrado, recibirás un enlace para restablecer tu contraseña."}

    async def reset_password(
        self, 
        data: ResetPasswordRequest
        ) -> MessageResponse:

        payload = TokenService().decode_token(data.token)
        
        if not payload or payload.get("token_kind") != "reset":
            raise PasswordResetTokenInvalid()
            
        user_id_str = payload.get("user_id")
        user = await UserService(self.session).get_by_id(UUID(user_id_str))
        
        if not user:
            raise PasswordResetTokenNotFound()
            
        if data.identifier not in [user.username, user.email]:
            raise PasswordResetTokenInvalid()

        await UserService(self.session).reset_password(user.id, data.new_password)
        
        return {"message": "Contraseña actualizada correctamente."}