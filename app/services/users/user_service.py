from typing import Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from sqlalchemy.orm import joinedload
from app.models.role import Role



class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.id == user_id))

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.username == username))

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.email == email))
    
    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        return await self.session.scalar(
            select(User).where(
                or_(
                    User.username == identifier,
                    User.email == identifier
                )
            )
        )
    
    async def get_with_role_and_permissions(self, identifier: str):
     result = await self.session.execute(
        select(User).options(
            joinedload(User.role).joinedload(Role.permissions)
        ).where(
            (User.username == identifier) | (User.email == identifier)
        )
    )
     return result.unique().scalar_one_or_none()