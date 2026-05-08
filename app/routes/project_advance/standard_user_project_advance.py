from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.core.enums import FileFolder
from app.models.user import User
from app.schemas.project_advance import ProjectAdvanceResponse
from app.services.FileService import FileService
from app.services.project_advance_service import ProjectAdvanceService

router = APIRouter(prefix="/projects", tags=["Project Advances"])


@router.post(
    "/{project_id}/advances",
    response_model=ProjectAdvanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_advance(
    project_id: UUID,
    file: UploadFile,
    description: str = Form(...),
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    upload = await FileService().upload(
        file,
        folder=FileFolder.PROJECT_ADVANCES,
        entity_id=project_id,
        allowed_types=FileService.IMAGES | FileService.DOCUMENTS,
    )

    return await ProjectAdvanceService(session).create(
        project_id,
        current_user.id,
        description=description,
        url=upload.url,
    )


@router.get("/{project_id}/advances", response_model=list[ProjectAdvanceResponse])
async def list_advances(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectAdvanceService(session).list_by_project(project_id)


@router.get("/{project_id}/advances/{number}", response_model=ProjectAdvanceResponse)
async def get_advance(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectAdvanceService(session).get_by_project_and_number(
        project_id, number
    )


@router.delete(
    "/{project_id}/advances/{number}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_advance(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    await ProjectAdvanceService(session).delete(project_id, number, current_user.id)
