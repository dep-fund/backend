from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.id == user_id))

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.username == username))

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.session.scalar(select(User).where(User.email == email))