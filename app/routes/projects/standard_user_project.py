from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreateRequest,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectService(session).create(current_user.id, data)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdateRequest,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectService(session).update(project_id, current_user.id, data)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
)
async def list_my_projects(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await ProjectService(session).list_by_user(
        current_user.id,
        page=page,
        page_size=page_size,
    )

    return PaginatedResponse[ProjectResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )


@router.get("/explore", response_model=PaginatedResponse[ProjectResponse])
async def explore_projects(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await ProjectService(session).explore(
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
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await ProjectService(session).get_approved(project_id)
