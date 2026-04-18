from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import UserType
from app.exceptions.role import RoleNotFound, RoleWithAssignedUsers
from app.models.role import Role
from app.schemas.role import RoleCreateRequest, RoleResponse

class RoleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: RoleCreateRequest) -> RoleResponse:
        role = Role(
            type=data.type,
        )

        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)

        return RoleResponse.model_validate(role)
    
    async def get_by_type(self, role_type: str) -> Role:
        role = await self.session.scalar(
            select(Role).where(Role.type == role_type)
        )
        if not role:
            raise RoleNotFound()
        
        return role

    async def get_by_id(self, id: UUID) -> Role:
        role = await self.session.scalar(
            select(Role).where(Role.id == id)
        )
        if not role:
            raise RoleNotFound()
        
        return role
    
    async def get_assigned_users(self, role_type: str) -> list:
        role = await self.get_by_type(role_type)

        await self.session.refresh(role, attribute_names=["users"])
        return role.users
    
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
    
    async def delete(self, type: str) -> dict:
        role = await self.get_by_type(type)
        await self.session.refresh(role, attribute_names=["users"])

        if role.users:
            raise RoleWithAssignedUsers()

        await self.session.delete(role)
        await self.session.commit()

        return {"detail": "Role deleted successfully"}