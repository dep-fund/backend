from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.enums import UserType
from app.core.security.hash_password import hash_password
from app.core.security.verify_password import verify_password
from app.models.user import AdminUser, User
from app.schemas.users.admin_user import (
    AdminUserChangePasswordRequest,
    AdminUserCreateRequest,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.services.role_service import RoleService
from app.services.users.user_service import UserService
from app.exceptions.users.user_exceptions import (
    UsernameAlreadyTaken,
    EmailAlreadyRegistered,
    UserNotFound,
    WrongCurrentPassword,
)
from app.schemas.users.standard_user import (
    StandardUserResponse
)


class AdminUserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._user_service = UserService(session)

    def _base_query(self):
        return (
            select(User)
            .join(AdminUser, AdminUser.id == User.id)
            .options(selectinload(User.admin))
            .where(User.type == UserType.ADMIN)
        )

    async def create(self, data: AdminUserCreateRequest) -> AdminUserResponse:
        if data.admin_secret_key != settings.ADMIN_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid secret key",
            )
        if await self._user_service.get_by_username(data.username):
            raise UsernameAlreadyTaken()
        if await self._user_service.get_by_email(data.email):
            raise EmailAlreadyRegistered()

        role = await RoleService(self.session).get_by_type(UserType.ADMIN)
        user = User(
            username=data.username,
            name=data.name,
            last_name=data.last_name,
            email=data.email,
            password=hash_password(data.password),
            image=data.image,
            type=UserType.ADMIN,
            role_id=role.id,
        )

        self.session.add(user)
        await self.session.flush()
        self.session.add(AdminUser(id=user.id))
        await self.session.commit()
        await self.session.refresh(user)

        return AdminUserResponse.model_validate(user)

    async def update(self, user_id: UUID, data: AdminUserUpdateRequest) -> AdminUserResponse:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)

        return AdminUserResponse.model_validate(user)

    async def change_password(
        self, user_id: UUID, data: AdminUserChangePasswordRequest
    ) -> AdminUserResponse:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        if not verify_password(data.old_password, user.password):
            raise WrongCurrentPassword()

        user.password = hash_password(data.new_password)
        await self.session.commit()
        await self.session.refresh(user)

        return AdminUserResponse.model_validate(user)

    async def delete(self, user_id: UUID) -> dict:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        await self.session.delete(user)
        await self.session.commit()

        return {"detail": "User deleted successfully"}
    
    async def toggle_user_block(self, user_id: UUID) -> StandardUserResponse:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()

        user.blocked = not user.blocked
        await self.session.commit()
        await self.session.refresh(user)

        return StandardUserResponse.model_validate(user)
    