from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.investment import (
    InvestmentCreateRequest,
    InvestmentResponse,
    ProjectInvestmentStats,
)
from app.schemas.pagination import PaginatedResponse
from app.services.investment_service import InvestmentService

router = APIRouter(prefix="/investments", tags=["Investments"])


@router.post(
    "/{project_id}",
    response_model=InvestmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_investment(
    project_id: UUID,
    data: InvestmentCreateRequest,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await InvestmentService(session).create(current_user.id, project_id, data)


@router.get("/me", response_model=PaginatedResponse[InvestmentResponse])
async def list_my_investments(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await InvestmentService(session).list_by_user(
        current_user.id, page=page, page_size=page_size
    )
    return PaginatedResponse[InvestmentResponse](
        total=total, page=page, page_size=page_size, results=items
    )


@router.get(
    "/project/{project_id}", response_model=PaginatedResponse[InvestmentResponse]
)
async def list_project_investments(
    project_id: UUID,
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    total, items = await InvestmentService(session).list_by_project(
        project_id, page=page, page_size=page_size
    )
    return PaginatedResponse[InvestmentResponse](
        total=total, page=page, page_size=page_size, results=items
    )


@router.get("/project/{project_id}/stats", response_model=ProjectInvestmentStats)
async def get_project_investment_stats(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await InvestmentService(session).get_project_stats(project_id)
