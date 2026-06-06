from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project_document import ProjectDocumentResponse
from app.services.project_document_service import ProjectDocumentService

router = APIRouter(prefix="/admin/projects",tags=["Administrators - Projects Documents"])

@router.get("/{project_id}/documents", response_model=list[ProjectDocumentResponse])
async def list_documents(
    project_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectDocumentService(session).admin_list_by_project(project_id)

@router.get("/{project_id}/documents/{number}", response_model=ProjectDocumentResponse)
async def get_document(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectDocumentService(session).admin_get_by_project_and_number(project_id, number)