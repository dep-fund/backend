from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.permission import PermissionNotFound, PermissionRoleAlreadyAssigned, PermissionRoleNotFound
from app.models.permission import Permission
from app.models.permission_role import PermissionRole
from app.models.role import Role
from app.schemas.permission import DetailPermissionRoleResponse, PermissionCreateRequest, PermissionResponse, PermissionRoleCreateRequest, PermissionRoleDeleteRequest, PermissionRoleResponse
from app.services.role_service import RoleService

class PermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

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

    async def get_by_id(self, id: str) -> Permission:
        permission = await self.session.scalar(
            select(Permission).where(Permission.id == id)
        )
        if not permission:
            raise PermissionNotFound()
        
        return permission
    
    async def get_permission_role(self, role_id: UUID, permission_id: UUID) -> Permission:
        permission_role = await self.session.scalar(
            select(PermissionRole).where(
                PermissionRole.role_id == role_id,
                PermissionRole.permission_id == permission_id
            )
        )
        return permission_role
    
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
    
    
    async def assign_to_role(self, data: PermissionRoleCreateRequest) -> DetailPermissionRoleResponse:
        await RoleService(self.session).get_by_id(data.role_id)
        await PermissionService(self.session).get_by_id(data.permission_id)
        permission_role = await self.get_permission_role(role_id=data.role_id, permission_id=data.permission_id)
        if permission_role is not None:
            raise PermissionRoleAlreadyAssigned()
        
        relation = PermissionRole(
            role_id=data.role_id,
            permission_id=data.permission_id,
        )

        self.session.add(relation)
        await self.session.commit()
        await self.session.refresh(relation)

        return PermissionRoleResponse(
            role_id=relation.role_id,
            permission_id=relation.permission_id,
        )
    
    async def delete_assigned_permission_role(self, data: PermissionRoleDeleteRequest) -> dict:
        await RoleService(self.session).get_by_id(data.role_id)
        await PermissionService(self.session).get_by_id(data.permission_id)

        permission_role = await self.get_permission_role(
            role_id=data.role_id,
            permission_id=data.permission_id
        )

        if permission_role is None:
            raise PermissionRoleNotFound()

        await self.session.delete(permission_role)
        await self.session.commit()

        return {"detail": "Permission from role deleted successfully"}
    
    async def list_assigned_permissions_roles(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[int, List[DetailPermissionRoleResponse]]:

        query = (
            select(
                Role.id.label("role_id"),
                Role.type.label("role"),
                Permission.id.label("permission_id"),
                Permission.type.label("permission"),
            )
            .select_from(PermissionRole)
            .join(Role, Role.id == PermissionRole.role_id)
            .join(Permission, Permission.id == PermissionRole.permission_id)
        )

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        result = await self.session.execute(
            query.offset((page - 1) * page_size).limit(page_size)
        )

        rows = result.all()

        return total or 0, [
            DetailPermissionRoleResponse(
                role_id=row.role_id,
                permission_id=row.permission_id,
                role=row.role,
                permission=row.permission,
            )
            for row in rows
        ]