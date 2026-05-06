from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import ProjectState
from app.models.project_document import ProjectDocument
from app.schemas.project_document import ProjectDocumentCreate, ProjectDocumentResponse
from app.services.project_service import ProjectService
from app.exceptions.project_document import DocumentNotFound, UnauthorizedDocumentAccess, DocumentNotDeleted

class ProjectDocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._project_service = ProjectService(session)

    async def create(self, project_id: UUID, user_id: UUID, data: ProjectDocumentCreate) -> ProjectDocumentResponse:
        project = await self._project_service._get_project(project_id)
        if project.user_id != user_id:
            raise UnauthorizedDocumentAccess()

        max_number = await self.session.scalar(
            select(func.max(ProjectDocument.number)).where(
                ProjectDocument.project_id == project_id
            )
        )
        new_number = (max_number or 0) + 1

        doc = ProjectDocument(
            project_id=project_id,
            number=new_number,
            url=data.url,
        )
        self.session.add(doc)
        await self.session.commit()
        return ProjectDocumentResponse.model_validate(doc)
    
    async def _validate_project_owner(self, project_id: UUID, user_id: UUID) :
        project = await self._project_service._get_project(project_id)
        if project.user_id != user_id:
            raise UnauthorizedDocumentAccess()
        return project
    
    async def _get_document(self, project_id: UUID, number: int) -> ProjectDocument:
        doc = await self.session.scalar(
            select(ProjectDocument).where(
                ProjectDocument.project_id == project_id,
                ProjectDocument.number == number
            )
        )
        if not doc:
            raise DocumentNotFound()
        return doc
    
    async def list_by_project(self, project_id: UUID, user_id: UUID) -> list[ProjectDocumentResponse]:
        await self._validate_project_owner(project_id, user_id)

        result = await self.session.scalars(
            select(ProjectDocument).where(ProjectDocument.project_id == project_id).order_by(ProjectDocument.number)
        )
        return [ProjectDocumentResponse.model_validate(doc) for doc in result.all()]

    async def admin_list_by_project(self, project_id: UUID) -> list[ProjectDocumentResponse]:
        await self._project_service._get_project(project_id)  

        result = await self.session.scalars(
            select(ProjectDocument).where(ProjectDocument.project_id == project_id).order_by(ProjectDocument.number)
        )
        return [ProjectDocumentResponse.model_validate(doc) for doc in result.all()]
    
    async def get_by_project_and_number(self, project_id: UUID, number: int, user_id: UUID) -> ProjectDocumentResponse:
        await self._validate_project_owner(project_id, user_id)
        doc = await self._get_document(project_id, number)
        return ProjectDocumentResponse.model_validate(doc)
    
    async def admin_get_by_project_and_number(self, project_id: UUID, number: int) -> ProjectDocumentResponse:
        await self._project_service._get_project(project_id)
        doc = await self._get_document(project_id, number)
        return ProjectDocumentResponse.model_validate(doc)
    
    async def delete(self, project_id: UUID, number: int, user_id: UUID) -> None:
        project = await self._validate_project_owner(project_id, user_id)
        if project.state == ProjectState.APPROVED:
            raise DocumentNotDeleted()

        doc = await self._get_document(project_id, number)

        await self.session.delete(doc)
        await self.session.commit()
    