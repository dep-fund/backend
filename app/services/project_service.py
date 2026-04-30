from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import ProjectState
from app.models.project import Project
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
)

from app.exceptions.project import (
    ProjectNotFound,
    UnauthorizedProjectAccess,
)
from app.services.category_service import CategoryService


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._category_service = CategoryService(session)

    def _base_query(self):
        return select(Project).options(selectinload(Project.categories))
    
    async def _get_project(self, project_id: UUID) -> Project:
        project = await self.session.scalar(
            self._base_query().where(Project.id == project_id)
        )
        if not project:
            raise ProjectNotFound()
        return project
    
    async def _paginate(
        self, query, page: int, page_size: int
    ) -> Tuple[int, List[ProjectResponse]]:
        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        projects = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()
        return total or 0, [ProjectResponse.model_validate(p) for p in projects]

    async def create(self, user_id: UUID, data: ProjectCreateRequest) -> ProjectResponse:
        project = Project(
            name=data.name,
            description=data.description,
            total_amount=data.total_amount,
            ubication=data.ubication,
            user_id=user_id,
        )

        if data.category_ids:
            categories = await self._category_service.get_categories_by_ids(data.category_ids)
            project.categories = categories

        self.session.add(project)
        await self.session.commit()
        project = await self._get_project(project.id)

        return ProjectResponse.model_validate(project)

    async def update(
        self,
        project_id: UUID,
        user_id: UUID,
        data: ProjectUpdateRequest,
    ) -> ProjectResponse:
        project = await self._get_project(project_id)

        if project.user_id != user_id:
            raise UnauthorizedProjectAccess()

        for field, value in data.model_dump(exclude_none=True).items():
            if field != "category_ids":
                setattr(project, field, value)

        if data.category_ids is not None:
            categories = await self._category_service.get_categories_by_ids(data.category_ids)
            project.categories = categories

        await self.session.commit()
        project = await self._get_project(project.id)
        
        return ProjectResponse.model_validate(project)

    async def list_by_user(self, user_id: UUID, page: int = 1, page_size: int = 10) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query().where(Project.user_id == user_id)
        return await self._paginate(query, page, page_size)

    async def get_approved(self, project_id: UUID, user_id: UUID) -> ProjectResponse:
        """Access: only for your own projects; if you are not the owner, only return the project if they are approved."""
        project = await self._get_project(project_id)

        if project.user_id == user_id or project.state == ProjectState.APPROVED:
            return ProjectResponse.model_validate(project)

        raise UnauthorizedProjectAccess()
    
    async def explore(self, page: int = 1, page_size: int = 10) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query().where(Project.state == ProjectState.APPROVED)
        return await self._paginate(query, page, page_size)
    
    async def admin_get(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_project(project_id)
        return ProjectResponse.model_validate(project)

    async def admin_list(self, page: int = 1, page_size: int = 10) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query()
        return await self._paginate(query, page, page_size)