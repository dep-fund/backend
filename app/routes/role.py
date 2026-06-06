from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.role import RoleCreateRequest, RoleResponse
from app.services.role_service import RoleService
from app.core.dependencies.user_dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/role", tags=["Administrators - Roles"])


@router.post("", response_model=RoleResponse)
async def create(
    data: RoleCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await RoleService(session).create(data)

@router.get(
    "",
    response_model=PaginatedResponse[RoleResponse],
)
async def list_roles(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    total, items = await RoleService(session).list(
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[RoleResponse](
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
    return await RoleService(session).delete(type)
    