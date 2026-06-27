from decimal import Decimal
from typing import List, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enums import ProjectState, InvestmentSource
from app.models.investment import Investment
from app.models.project import Project
from app.models.token_project import TokenProject
from app.exceptions.project import ProjectNotFound
from app.exceptions.investment import (
    ProjectNotInvestable,
    InvalidInvestmentAmount,
    InvestmentExceedsHardCap,
    InsufficientHoldings,
)
from app.schemas.investment import (
    InvestmentCreateRequest,
    InvestmentResponse,
    ProjectInvestmentStats,
)

from app.services.transaction_service import TransactionService


class InvestmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_project(self, project_id: UUID) -> Project:
        project = await self.session.scalar(
            select(Project).where(Project.id == project_id)
        )
        if not project:
            raise ProjectNotFound()
        return project

    async def _get_token_id_for_project(self, project_id: UUID) -> UUID:
        token_project = await self.session.scalar(
            select(TokenProject).where(TokenProject.project_id == project_id)
        )
        if not token_project:
            raise ProjectNotInvestable()
        return token_project.token_id

    async def _get_project_id_for_token(self, token_id: UUID) -> UUID:
        token_project = await self.session.scalar(
            select(TokenProject).where(TokenProject.token_id == token_id)
        )
        if not token_project:
            raise ProjectNotInvestable()
        return token_project.project_id

    async def _get_raised_amount(self, project_id: UUID) -> Decimal:
        """Solo cuenta inversiones OFFERING: la compraventa en marketplace
        no representa plata nueva ingresando al proyecto."""
        result = await self.session.scalar(
            select(
                func.coalesce(
                    func.sum(Investment.token_quantity * Investment.unit_price), 0
                )
            ).where(
                Investment.project_id == project_id,
                Investment.source == InvestmentSource.offering,
            )
        )
        return Decimal(result or 0)

    # ---------- Inversión inicial (Offering) ----------

    async def create(
        self,
        user_id: UUID,
        project_id: UUID,
        data: InvestmentCreateRequest,
    ) -> InvestmentResponse:
        project = await self._get_project(project_id)

        if project.state != ProjectState.APPROVED:
            raise ProjectNotInvestable()

        if data.token_quantity <= 0 or data.unit_price <= 0:
            raise InvalidInvestmentAmount()

        token_id = await self._get_token_id_for_project(project_id)

        amount = data.token_quantity * data.unit_price
        already_raised = await self._get_raised_amount(project_id)

        if already_raised + amount > project.total_amount:
            raise InvestmentExceedsHardCap()

        investment = Investment(
            user_id=user_id,
            project_id=project_id,
            token_id=token_id,
            token_quantity=data.token_quantity,
            unit_price=data.unit_price,
            source=InvestmentSource.offering,
            is_active=True,
            tx_hash=data.tx_hash,
        )
        self.session.add(investment)
        await self.session.commit()
        await self.session.refresh(investment)

        TransactionService.create_investment(
            tx_hash=data.tx_hash,
            wallet_id=data.wallet_id,
            project_id=project_id,
        )
        return InvestmentResponse.model_validate(investment)

    # ---------- Hooks para Marketplace (llamados desde TradeService) ----------

    async def register_marketplace_purchase(
        self,
        buyer_id: UUID,
        token_id: UUID,
        amount: Decimal,
        unit_price: Decimal,
        tx_hash: str | None = None,
    ) -> Investment:
        """Crea el Investment del comprador cuando se confirma un Trade."""
        project_id = await self._get_project_id_for_token(token_id)

        investment = Investment(
            user_id=buyer_id,
            project_id=project_id,
            token_id=token_id,
            token_quantity=amount,
            unit_price=unit_price,
            source=InvestmentSource.marketplace,
            is_active=True,
            tx_hash=tx_hash,
        )
        self.session.add(investment)
        await self.session.flush()
        return investment

    async def consume_holdings(
        self, user_id: UUID, token_id: UUID, amount: Decimal
    ) -> None:
        """Descuenta `amount` de las inversiones activas del vendedor para ese
        token, en orden FIFO (más viejas primero). Marca is_active=False en
        las que se agotan; actualiza token_quantity en la que queda parcial."""
        holdings = (
            await self.session.scalars(
                select(Investment)
                .where(
                    Investment.user_id == user_id,
                    Investment.token_id == token_id,
                    Investment.is_active.is_(True),
                )
                .order_by(Investment.created_at.asc())
                .with_for_update()
            )
        ).all()

        remaining = amount
        for holding in holdings:
            if remaining <= 0:
                break
            if holding.token_quantity <= remaining:
                remaining -= holding.token_quantity
                holding.token_quantity = Decimal(0)
                holding.is_active = False
            else:
                holding.token_quantity -= remaining
                remaining = Decimal(0)

        if remaining > 0:
            raise InsufficientHoldings()

    # ---------- Listados y stats ----------

    async def list_by_user(
        self, user_id: UUID, page: int = 1, page_size: int = 10
    ) -> Tuple[int, List[InvestmentResponse]]:
        query = select(Investment).where(Investment.user_id == user_id)
        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        rows = (
            await self.session.scalars(
                query.order_by(Investment.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()
        return total or 0, [InvestmentResponse.model_validate(i) for i in rows]

    async def list_by_project(
        self, project_id: UUID, page: int = 1, page_size: int = 10
    ) -> Tuple[int, List[InvestmentResponse]]:
        query = select(Investment).where(Investment.project_id == project_id)
        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        rows = (
            await self.session.scalars(
                query.order_by(Investment.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).all()
        return total or 0, [InvestmentResponse.model_validate(i) for i in rows]

    async def get_project_stats(self, project_id: UUID) -> ProjectInvestmentStats:
        project = await self._get_project(project_id)

        raised_amount = await self._get_raised_amount(project_id)
        investors_count = await self.session.scalar(
            select(func.count(func.distinct(Investment.user_id))).where(
                Investment.project_id == project_id,
                Investment.is_active.is_(True),
            )
        )

        progress_pct = Decimal(0)
        if project.total_amount and project.total_amount > 0:
            progress_pct = min(
                Decimal(100), (raised_amount / project.total_amount) * 100
            )

        return ProjectInvestmentStats(
            raised_amount=raised_amount,
            investors_count=investors_count or 0,
            progress_pct=progress_pct,
        )
