from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project_advance import ProjectAdvance
from app.schemas.project_advance import ProjectAdvanceCreate, ProjectAdvanceResponse
from app.services.project_service import ProjectService
from app.exceptions.project_advance import AdvanceNotFound, UnauthorizedAdvanceAccess

class ProjectAdvanceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._project_service = ProjectService(session)

    async def create(self, project_id: UUID, user_id: UUID, data: ProjectAdvanceCreate) -> ProjectAdvanceResponse:
        project = await self._project_service._get_project(project_id)
        if project.user_id != user_id:
            raise UnauthorizedAdvanceAccess()

        max_number = await self.session.scalar(
            select(func.max(ProjectAdvance.number)).where(
                ProjectAdvance.project_id == project_id
            )
        )
        new_number = (max_number or 0) + 1

        adv = ProjectAdvance(
            project_id=project_id,
            number=new_number,
            description= data.description,
            url=data.url,
        )
        self.session.add(adv)
        await self.session.commit()
        return ProjectAdvanceResponse.model_validate(adv)
    
    async def _validate_project_owner(self, project_id: UUID, user_id: UUID):
        project = await self._project_service._get_project(project_id)
        if project.user_id != user_id:
            raise UnauthorizedAdvanceAccess()
        return project
    
    async def _get_advance(self, project_id: UUID, number: int) -> ProjectAdvance:
        adv = await self.session.scalar(
            select(ProjectAdvance).where(
                ProjectAdvance.project_id == project_id,
                ProjectAdvance.number == number
            )
        )
        if not adv:
            raise AdvanceNotFound()
        return adv
    
    async def list_by_project(self, project_id: UUID, user_id: UUID) -> list[ProjectAdvanceResponse]:
        await self._validate_project_owner(project_id, user_id)

        result = await self.session.scalars(
            select(ProjectAdvance).where(ProjectAdvance.project_id == project_id).order_by(ProjectAdvance.number)
        )
        return [ProjectAdvanceResponse.model_validate(adv) for adv in result.all()]

    async def admin_list_by_project(self, project_id: UUID) -> list[ProjectAdvanceResponse]:
        await self._project_service._get_project(project_id)  

        result = await self.session.scalars(
            select(ProjectAdvance).where(ProjectAdvance.project_id == project_id).order_by(ProjectAdvance.number)
        )
        return [ProjectAdvanceResponse.model_validate(adv) for adv in result.all()]
    
    async def get_by_project_and_number(self, project_id: UUID, number: int, user_id: UUID) -> ProjectAdvanceResponse:
        await self._validate_project_owner(project_id, user_id)
        adv = await self._get_advance(project_id, number)
        return ProjectAdvanceResponse.model_validate(adv)
    
    async def admin_get_by_project_and_number(self, project_id: UUID, number: int) -> ProjectAdvanceResponse:
        await self._project_service._get_project(project_id)
        adv = await self._get_advance(project_id, number)
        return ProjectAdvanceResponse.model_validate(adv)
    
    async def delete(self, project_id: UUID, number: int, user_id: UUID) -> None:
        await self._validate_project_owner(project_id, user_id)
        adv = await self._get_advance(project_id, number)

        await self.session.delete(adv)
        await self.session.commit()
