from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectResponse
from app.services.project_service import ProjectService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin/projects",tags=["Administrators - Projects"])


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
)
async def list_all(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await ProjectService(session).admin_list(
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get(
    project_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectService(session).admin_get(project_id)