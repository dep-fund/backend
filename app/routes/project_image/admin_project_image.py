from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project_image import ProjectImageResponse
from app.services.project_image_service import ProjectImageService

router = APIRouter(prefix="/admin/projects", tags=["Administrators - Projects Images"])


@router.get("/{project_id}/images", response_model=list[ProjectImageResponse])
async def list_images(
    project_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectImageService(session).admin_list_by_project(project_id)


@router.get("/{project_id}/images/{number}", response_model=ProjectImageResponse)
async def get_image(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectImageService(session).admin_get_by_project_and_number(
        project_id, number
    )
