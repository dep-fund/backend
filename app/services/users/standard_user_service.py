from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import UserType
from app.core.security.hash_password import hash_password
from app.core.security.verify_password import verify_password
from app.models.user import StandardUser, User
from app.schemas.users.standard_user import (
    StandardUserChangePasswordRequest,
    StandardUserRegisterRequest,
    StandardUserResponse,
    StandardUserUpdateRequest,
)
from app.services.role_service import RoleService
from app.services.users.user_service import UserService

from app.exceptions.users.user_exceptions import (
    UsernameAlreadyTaken,
    EmailAlreadyRegistered,
    UserNotFound,
    WrongCurrentPassword,
)


class StandardUserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._user_service = UserService(session)

    def _base_query(self):
        return (
            select(User)
            .join(StandardUser, StandardUser.id == User.id)
            .options(selectinload(User.standard))
            .where(User.type == UserType.STANDARD)
        )

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        blocked: Optional[bool] = None,
    ) -> tuple[int, list[StandardUserResponse]]:
        query = self._base_query()

        if search:
            query = query.where(
                User.username.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
            )
        if is_active is not None:
            query = query.where(User.activated == is_active)
        if blocked is not None:
            query = query.where(User.blocked == blocked)

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        users = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()

        return total or 0, [StandardUserResponse.model_validate(u) for u in users]

    async def register(self, data: StandardUserRegisterRequest) -> StandardUserResponse:
        if await self._user_service.get_by_username(data.username):
            raise UsernameAlreadyTaken()
        if await self._user_service.get_by_email(data.email):
            raise EmailAlreadyRegistered()

        role = await RoleService(self.session).get_by_type(UserType.STANDARD)
        user = User(
            username=data.username,
            name=data.name,
            last_name=data.last_name,
            birthdate=data.birthdate,
            email=data.email,
            password=hash_password(data.password),
            image=data.image,
            type=UserType.STANDARD,
            role_id=role.id,
        )

        self.session.add(user)
        await self.session.flush()
        self.session.add(StandardUser(id=user.id))
        await self.session.commit()
        await self.session.refresh(user)

        return StandardUserResponse.model_validate(user)

    async def update(self, user_id: UUID, data: StandardUserUpdateRequest) -> StandardUserResponse:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await self.session.commit()
        await self.session.refresh(user)
        return StandardUserResponse.model_validate(user)

    async def change_password(
        self, user_id: UUID, data: StandardUserChangePasswordRequest
    ) -> StandardUserResponse:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        if not verify_password(data.old_password, user.password):
            raise WrongCurrentPassword()
        
        user.password = hash_password(data.new_password)
        await self.session.commit()
        await self.session.refresh(user)
        return StandardUserResponse.model_validate(user)

    async def delete(self, user_id: UUID) -> dict:
        user = await self._user_service.get_by_id(user_id)
        if not user:
            raise UserNotFound()
        user.activated = False

        self.session.add(user)
        await self.session.commit()

        return {"detail": "User deleted successfully"}