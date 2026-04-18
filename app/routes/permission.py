from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.enums import UserType
from app.schemas.pagination import PaginatedResponse
from app.schemas.permission import PermissionResponse, PermissionCreateRequest
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.services.permission_service import PermissionService

router = APIRouter(prefix="/admin/permission", tags=["Administrators - Permissions"])


@router.post("", response_model=PermissionResponse)
async def create(
    data: PermissionCreateRequest,
    session: AsyncSession = Depends(get_session),
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
):
    return await PermissionService(session).delete(type)