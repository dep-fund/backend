import asyncio
from decimal import Decimal
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import ProjectState
from app.models.project import Project
from app.models.token import Token
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectUpdateAdminRequest,
)

from app.exceptions.project import (
    ProjectNameAlreadyExists,
    ProjectNotFound,
    ProjectSuffixAlreadyExists,
    UnauthorizedProjectAccess,
    ProjectNotPending,
    MissingMandatoryProjectInfo,
)
from app.models.project_evaluation import ProjectEvaluation
from app.services.blockchain.contracts.dividends_service import DividendsService
from app.services.blockchain.contracts.dpf_token_service import DpfTokenService
from app.services.blockchain.contracts.offering_service import OfferingService
from app.services.category_service import CategoryService
from app.services.mail_service import MailService
from app.core.config import settings
from app.services.token_service import TokenContractService


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

    async def create(
        self,
        user_id: UUID,
        data: ProjectCreateRequest,
    ) -> ProjectResponse:
        existing_name = await self.session.scalar(
            select(Project).where(Project.name == data.name)
        )
        if existing_name:
            raise ProjectNameAlreadyExists()

        if data.suffix:
            existing_suffix = await self.session.scalar(
                select(Project).where(Project.suffix == data.suffix)
            )
            if existing_suffix:
                raise ProjectSuffixAlreadyExists()

            existing_token_suffix = await self.session.scalar(
                select(Token).where(Token.suffix == data.suffix)
            )
            if existing_token_suffix:
                raise ProjectSuffixAlreadyExists()

        annual_benefits = None
        roi = None

        if data.annual_gross_profit is not None and data.annual_expenses is not None:
            annual_benefits = data.annual_gross_profit - data.annual_expenses
            if data.total_amount and data.total_amount > 0:
                roi = (annual_benefits / data.total_amount) * 100

        project = Project(
            name=data.name,
            description=data.description,
            total_amount=data.total_amount,
            ubication=data.ubication,
            min_amount=data.min_amount,
            annual_expenses=data.annual_expenses,
            annual_gross_profit=data.annual_gross_profit,
            annual_benefits=annual_benefits,
            roi=roi,
            suffix=data.suffix,
            user_id=user_id,
            estimated_development_days=data.estimated_development_days,
        )

        if data.category_ids:
            categories = await self._category_service.get_categories_by_ids(
                data.category_ids
            )
            project.categories = categories

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)

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

        for field, value in data.model_dump(exclude_unset=True).items():
            if field != "category_ids":
                setattr(project, field, value)

        if data.category_ids is not None:
            categories = await self._category_service.get_categories_by_ids(
                data.category_ids
            )
            project.categories = categories

        await self.session.commit()
        await self.session.refresh(project)

        project = await self._get_project(project.id)
        return ProjectResponse.model_validate(project)

    async def update_by_admin(
        self,
        project_id: UUID,
        admin_id: UUID,
        data: ProjectUpdateAdminRequest,
    ) -> ProjectResponse:
        project = await self._get_project(project_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            if field != "category_ids":
                setattr(project, field, value)

        if data.category_ids is not None:
            categories = await self._category_service.get_categories_by_ids(
                data.category_ids
            )
            project.categories = categories

        await self.session.commit()
        await self.session.refresh(project)

        project = await self._get_project(project.id)
        return ProjectResponse.model_validate(project)

    async def list_by_user(
        self, user_id: UUID, page: int = 1, page_size: int = 10
    ) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query().where(Project.user_id == user_id)
        return await self._paginate(query, page, page_size)

    async def get_approved(self, project_id: UUID, user_id: UUID) -> ProjectResponse:
        """Access: only for your own projects; if you are not the owner, only return the project if they are approved."""
        project = await self._get_project(project_id)

        if project.user_id == user_id or project.state == ProjectState.APPROVED:
            return ProjectResponse.model_validate(project)

        raise UnauthorizedProjectAccess()

    async def explore(
        self, page: int = 1, page_size: int = 10
    ) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query().where(Project.state == ProjectState.APPROVED)
        return await self._paginate(query, page, page_size)

    async def admin_get(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_project(project_id)
        return ProjectResponse.model_validate(project)

    async def admin_list(
        self, page: int = 1, page_size: int = 10
    ) -> Tuple[int, List[ProjectResponse]]:
        query = self._base_query()
        return await self._paginate(query, page, page_size)

    async def evaluate(
        self, project_id: UUID, admin_id: UUID, is_approved: bool, reason: str = None
    ) -> ProjectResponse:
        print("MARKETPLACE: ", settings.MARKETPLACE_ADDRESS)
        print("FACTORY: ", settings.FACTORY_ADDRESS)
        project = await self.session.scalar(
            self._base_query()
            .options(selectinload(Project.user))
            .where(Project.id == project_id)
        )
        if not project:
            raise ProjectNotFound()

        if project.state != ProjectState.PENDING:
            raise ProjectNotPending()

        if is_approved:
            if (
                not project.name
                or not project.description
                or project.total_amount is None
            ):
                raise MissingMandatoryProjectInfo()
            if not project.ubication:
                raise MissingMandatoryProjectInfo()
            if not project.categories or len(project.categories) == 0:
                raise MissingMandatoryProjectInfo()

            project.state = ProjectState.APPROVED
            new_state = ProjectState.APPROVED
            dpf_token_service = DpfTokenService()
            token_address = dpf_token_service.create_project_token(
                name=project.name,
                suffix=project.suffix,
                supply=settings.PROJECT_TOKEN_SUPPLY,
            )

            offering_service = OfferingService()
            offering_address = offering_service.deploy(
                dpf_token=token_address,
                soft_cap=project.min_amount,
                hard_cap=project.total_amount,
                token_price=Decimal(
                    project.total_amount / settings.PROJECT_TOKEN_SUPPLY
                ),
                deadline_seconds=settings.OFFERING_DEADLINE_SECONDS,
            )

            dividends_service = DividendsService()
            dividend_address = dividends_service.deploy(
                dpf_token=token_address,
                issuer=settings.PLATFORM_ADDRESS,
                offering=offering_address,
            )
            project.offering_address = offering_address
            project.dividend_address = dividend_address

            dpf_token_service.set_offering(token_address, offering_address)
            dpf_token_service.transfer_to_offering(
                token_address, offering_address, settings.PROJECT_TOKEN_SUPPLY
            )

            token_service = TokenContractService(self.session)
            token = await token_service.create_token(
                name=project.name,
                suffix=project.suffix,
                contract_address=token_address,
            )
            await token_service.create_token_project(
                token_id=token.id,
                project_id=project_id,
                total_supply=Decimal(settings.PROJECT_TOKEN_SUPPLY),
            )
            print("Deployed, Addresses: ")
            print("TOKEN: ", token_address)
            print("OFFERING: ", offering_address)
            print("DIVIDEND: ", dividend_address)
        else:
            project.state = ProjectState.REJECTED
            new_state = ProjectState.REJECTED

        evaluation = ProjectEvaluation(
            project_id=project_id,
            admin_id=admin_id,
            description=reason,
            state=new_state,
        )
        self.session.add(evaluation)

        await self.session.commit()
        await self.session.refresh(project)

        mail_service = MailService()
        try:
            await asyncio.to_thread(
                mail_service.send_project_status_email,
                email=project.user.email,
                project_name=project.name,
                is_approved=is_approved,
                rejection_reason=reason,
            )
        except Exception:
            pass

        return ProjectResponse.model_validate(project)
