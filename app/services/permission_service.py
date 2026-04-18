from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import UserType
from app.exceptions.permission import PermissionNotFound
from app.models.permission import Permission
from app.schemas.permission import PermissionCreateRequest, PermissionResponse
from app.services.users.user_service import UserService

class PermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._user_service = UserService(session)

    async def create(self, data: PermissionCreateRequest) -> PermissionResponse:
        permission = Permission(
            type=data.type,
        )

        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)

        return PermissionResponse.model_validate(permission)
    
    async def get_by_type(self, permission_type: str) -> Permission:
        permission = await self.session.scalar(
            select(Permission).where(Permission.type == permission_type)
        )
        if not permission:
            raise PermissionNotFound()
        
        return permission
    
    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
    ) -> tuple[int, List[PermissionResponse]]:

        query = select(Permission)

        if search:
            query = query.where(Permission.type.ilike(f"%{search}%"))

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        permissions = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()

        return total or 0, [PermissionResponse.model_validate(p) for p in permissions]
    
    async def delete(self, type: str) -> dict:
        permission = await self.get_by_type(type)

        await self.session.delete(permission)
        await self.session.commit()

        return {"detail": "Permission deleted successfully"}