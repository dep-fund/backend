from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project_image import ProjectImage
from app.schemas.project_image import ProjectImageResponse
from app.services.project_service import ProjectService
from app.exceptions.project_image import (
    ImageNotFound,
    UnauthorizedImageAccess,
)


class ProjectImageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._project_service = ProjectService(session)

    async def create(
        self, project_id: UUID, user_id: UUID, *, url: str, public_id: str
    ) -> ProjectImageResponse:
        await self._validate_project_owner(project_id, user_id)

        max_number = await self.session.scalar(
            select(func.max(ProjectImage.number)).where(
                ProjectImage.project_id == project_id
            )
        )

        image = ProjectImage(
            project_id=project_id,
            number=(max_number or 0) + 1,
            url=url,
            public_id=public_id,
        )
        self.session.add(image)
        await self.session.commit()
        return ProjectImageResponse.model_validate(image)

    async def _validate_project_owner(self, project_id: UUID, user_id: UUID):
        project = await self._project_service._get_project(project_id)
        if project.user_id != user_id:
            raise UnauthorizedImageAccess()
        return project

    async def _get_image(self, project_id: UUID, number: int) -> ProjectImage:
        image = await self.session.scalar(
            select(ProjectImage).where(
                ProjectImage.project_id == project_id,
                ProjectImage.number == number,
            )
        )
        if not image:
            raise ImageNotFound()
        return image

    async def list_by_project(
        self, project_id: UUID, user_id: UUID
    ) -> list[ProjectImageResponse]:
        await self._project_service._get_project(project_id)

        result = await self.session.scalars(
            select(ProjectImage)
            .where(ProjectImage.project_id == project_id)
            .order_by(ProjectImage.number)
        )
        return [ProjectImageResponse.model_validate(img) for img in result.all()]

    async def delete(self, project_id: UUID, number: int, user_id: UUID) -> None:
        await self._validate_project_owner(project_id, user_id)
        image = await self._get_image(project_id, number)
        await self.session.delete(image)
        await self.session.commit()

    async def admin_list_by_project(
        self, project_id: UUID
    ) -> list[ProjectImageResponse]:
        await self._project_service._get_project(project_id)

        result = await self.session.scalars(
            select(ProjectImage)
            .where(ProjectImage.project_id == project_id)
            .order_by(ProjectImage.number)
        )
        return [ProjectImageResponse.model_validate(img) for img in result.all()]

    async def admin_get_by_project_and_number(
        self, project_id: UUID, number: int
    ) -> ProjectImageResponse:
        await self._project_service._get_project(project_id)
        image = await self._get_image(project_id, number)
        return ProjectImageResponse.model_validate(image)
