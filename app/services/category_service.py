from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse,
)

from app.exceptions.category import CategoryNotFound
from app.exceptions.category import CategoryHasProjects
from app.models.category_project import CategoryProject


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query(self):
        return select(Category)
    
    async def _get(self, category_id: UUID) -> Category:
        category = await self.session.scalar(
            select(Category).where(Category.id == category_id)
        )
        if not category:
            raise CategoryNotFound()
        return category

    async def create(self, data: CategoryCreateRequest) -> CategoryResponse:
        category = Category(
            name=data.name,
            description=data.description,
        )

        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)

        return CategoryResponse.model_validate(category)

    async def update(
        self, category_id: UUID, data: CategoryUpdateRequest
    ) -> CategoryResponse:
        category = await self._get(category_id)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(category, field, value)

        await self.session.commit()
        await self.session.refresh(category)

        return CategoryResponse.model_validate(category)

    async def get_by_id(self, category_id: UUID) -> CategoryResponse:
        category = await self._get(category_id)
        return CategoryResponse.model_validate(category)
    
    async def get_categories_by_ids(self, ids: List[UUID]) -> List[Category]:
        result = await self.session.scalars(
            select(Category).where(Category.id.in_(ids))
        )
        return result.all()

    async def list(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[int, List[CategoryResponse]]:
        query = select(Category)

        if search:
            query = query.where(Category.name.ilike(f"%{search}%"))

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        categories = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()

        return total or 0, [CategoryResponse.model_validate(c) for c in categories]
    
    
    async def delete(self, category_id: UUID):
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise CategoryNotFound()

        has_projects = await self.session.scalar(
            select(func.count()).where(CategoryProject.category_id == category_id)
        )

        if has_projects:
            raise CategoryHasProjects()

        await self.session.delete(category)
        await self.session.commit()