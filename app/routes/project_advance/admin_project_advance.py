from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project_advance import ProjectAdvanceResponse
from app.services.project_advance_service import ProjectAdvanceService

router = APIRouter(prefix="/admin/projects",tags=["Administrators - Projects Advances"])

@router.get("/{project_id}/advances", response_model=list[ProjectAdvanceResponse])
async def list_advances(
    project_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectAdvanceService(session).admin_list_by_project(project_id)

@router.get("/{project_id}/advances/{number}", response_model=ProjectAdvanceResponse)
async def get_advance(
    project_id: UUID,
    number: int,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectAdvanceService(session).admin_get_by_project_and_number(project_id, number)