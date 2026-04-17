from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.users.admin_user import (
    AdminUserChangePasswordRequest,
    AdminUserCreateRequest,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.schemas.users.standard_user import StandardUserResponse
from app.services.users.admin_user_service import AdminUserService
from app.services.users.standard_user_service import StandardUserService

router = APIRouter(prefix="/admin/users", tags=["Administrators - Users"])


@router.post("", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    data: AdminUserCreateRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AdminUserService(session).create(data)


@router.get("/me", response_model=AdminUserResponse)
async def get_me(current_user: User = Depends(get_current_admin_user)):
    return AdminUserResponse.model_validate(current_user)


@router.patch("/me", response_model=AdminUserResponse)
async def update_me(
    data: AdminUserUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminUserService(session).update(current_user.id, data)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: AdminUserChangePasswordRequest,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminUserService(session).change_password(current_user.id, data)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await AdminUserService(session).delete(current_user.id)

@router.get(
    "/users",
    response_model=PaginatedResponse[StandardUserResponse],
)
async def list_users(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await StandardUserService(session).list(
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[StandardUserResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )
