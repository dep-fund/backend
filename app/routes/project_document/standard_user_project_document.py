from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.project_document import ProjectDocumentCreate, ProjectDocumentResponse
from app.services.project_document_service import ProjectDocumentService

router = APIRouter(prefix="/projects", tags=["Project Documents"])

@router.post("/{project_id}/documents", response_model=ProjectDocumentResponse, status_code=status.HTTP_201_CREATED)
async def add_document(
    project_id: UUID,
    data: ProjectDocumentCreate,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectDocumentService(session).create(project_id, current_user.id, data)

@router.get("/{project_id}/documents", response_model=list[ProjectDocumentResponse])
async def list_documents(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectDocumentService(session).list_by_project(project_id, current_user.id)

@router.get("/{project_id}/documents/{number}", response_model=ProjectDocumentResponse)
async def get_document(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectDocumentService(session).get_by_project_and_number(project_id, number, current_user.id)

@router.delete("/{project_id}/documents/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    await ProjectDocumentService(session).delete(project_id, number, current_user.id)