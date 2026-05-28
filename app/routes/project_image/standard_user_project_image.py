from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.core.enums import FileFolder
from app.models.user import User
from app.schemas.project_image import ProjectImageResponse
from app.services.FileService import FileService
from app.services.project_image_service import ProjectImageService

router = APIRouter(prefix="/projects", tags=["Project Images"])


@router.post(
    "/{project_id}/images",
    response_model=ProjectImageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_image(
    project_id: UUID,
    file: UploadFile,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    upload = await FileService().upload(
        file,
        folder=FileFolder.PROJECT_IMAGES,
        entity_id=project_id,
        allowed_types=FileService.IMAGES,
    )
    return await ProjectImageService(session).create(
        project_id, current_user.id, url=upload.url, public_id=upload.public_id
    )


@router.get("/{project_id}/images", response_model=list[ProjectImageResponse])
async def list_images(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectImageService(session).list_by_project(
        project_id, current_user.id
    )


@router.delete("/{project_id}/images/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    await ProjectImageService(session).delete(project_id, number, current_user.id)
