from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.schemas.category import CategoryResponse
from app.schemas.pagination import PaginatedResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=PaginatedResponse[CategoryResponse],
)
async def list_categories(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    search: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_standard_user),
):
    total, items = await CategoryService(session).list(
        page=page,
        page_size=page_size,
        search=search,
    )

    return PaginatedResponse[CategoryResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_standard_user),
):
    return await CategoryService(session).get_by_id(category_id)