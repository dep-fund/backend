from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import UserType
from app.exceptions.role import RoleNotFound
from app.models.role import Role
from app.schemas.role import RoleCreateRequest, RoleResponse
from app.services.users.user_service import UserService

class RoleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._user_service = UserService(session)

    async def create(self, data: RoleCreateRequest) -> RoleResponse:
        role = Role(
            type=data.type,
        )

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        return RoleResponse.model_validate(role)
    
    async def get_by_type(self, role_type: UserType) -> Role:
        role = await self.session.scalar(
            select(Role).where(Role.type == role_type.value)
        )
        if not role:
            raise RoleNotFound()
        
        return role
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
    ) -> tuple[int, List[RoleResponse]]:
        
        query = select(Role)

        if search:
            query = query.where(Role.type.ilike(f"%{search}%"))

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        roles = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()

        return total or 0, [RoleResponse.model_validate(r) for r in roles]
    
    async def delete(self, type: UserType) -> dict:
        role = await self.get_by_type(type)

        await self.session.delete(role)
        await self.session.commit()

        return {"detail": "Role deleted successfully"}