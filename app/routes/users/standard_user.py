from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.core.enums import FileFolder
from app.models.user import User
from app.schemas.users.standard_user import (
    StandardUserChangePasswordRequest,
    StandardUserRegisterRequest,
    StandardUserResponse,
    StandardUserUpdateRequest,
)
from app.services.FileService import FileService
from app.services.users.standard_user_service import StandardUserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=StandardUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: StandardUserRegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    return await StandardUserService(session).register(data)


@router.get("/me", response_model=StandardUserResponse)
async def get_me(current_user: User = Depends(get_current_standard_user)):
    return StandardUserResponse.model_validate(current_user)


@router.patch("/me", response_model=StandardUserResponse)
async def update_me(
    data: StandardUserUpdateRequest,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await StandardUserService(session).update(current_user.id, data)


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: StandardUserChangePasswordRequest,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await StandardUserService(session).change_password(current_user.id, data)


@router.delete("/me")
async def delete_me(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await StandardUserService(session).delete(current_user.id)


@router.patch("/me/avatar", response_model=StandardUserResponse)
async def update_avatar(
    file: UploadFile,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    upload = await FileService().upload(
        file,
        folder=FileFolder.USER_AVATARS,
        allowed_types=FileService.IMAGES,
        max_size_mb=2,
    )
    return await StandardUserService(session).update_avatar(
        current_user.id, url=upload.url
    )
