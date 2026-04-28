from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.permission import DetailPermissionRoleResponse, PermissionResponse, PermissionCreateRequest, PermissionRoleCreateRequest, PermissionRoleDeleteRequest, PermissionRoleResponse,PermissionUpdateRequest
from app.core.dependencies.user_dependencies import get_current_admin_user,require_permission
from app.services.permission_service import PermissionService

from uuid import UUID


router = APIRouter(prefix="/admin/permission", tags=["Administrators - Permissions"])


@router.post("", response_model=PermissionResponse)
async def create(
    data: PermissionCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await PermissionService(session).create(data)

@router.get(
    "",
    response_model=PaginatedResponse[PermissionResponse],
)
async def list_permissions(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    total, items = await PermissionService(session).list(
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[PermissionResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )

@router.delete("", response_model=dict)
async def delete(
    type: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await PermissionService(session).delete(type)

@router.post("/assign-to-role", response_model=PermissionRoleResponse)
async def assign_permission_to_role(
    data: PermissionRoleCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await PermissionService(session).assign_to_role(data)

@router.delete("/assigned-permission", response_model=dict) # TODO: Separar responsabilidades con crud a parte para PermissionRole
async def delete_assigned_permission_role(
    data: PermissionRoleDeleteRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await PermissionService(session).delete_assigned_permission_role(data)

@router.get(
    "/role-permissions",
    response_model=PaginatedResponse[DetailPermissionRoleResponse],
)
async def list_role_permissions(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    total, items = await PermissionService(session).list_assigned_permissions_roles(
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[DetailPermissionRoleResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )


@router.patch("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: UUID,
    data: PermissionUpdateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_permission("permission:edit")),
):
    return await PermissionService(session).update(permission_id, data)