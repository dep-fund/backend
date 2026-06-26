import asyncio
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import TransactionType
from app.models.project import Project
from app.models.token_project import TokenProject
from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.schemas.report import (
    FundraisingReport,
    FundraisingSummary,
    ProjectFundraisingDetail,
)
from app.services.blockchain.contracts.offering_service import OfferingService


class ReportService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_fundraising_report(self) -> FundraisingReport:
        projects = await self._get_all_projects()

        projects_with_chain_data = await asyncio.gather(
            *[self._enrich_with_chain_data(p) for p in projects],
            return_exceptions=True,
        )

        details: list[ProjectFundraisingDetail] = []
        for result in projects_with_chain_data:
            if isinstance(result, Exception):
                continue
            details.append(result)

        summary = await self._compute_summary(details)

        return FundraisingReport(summary=summary, projects=details)

    async def _get_all_projects(self):
        result = await self.session.scalars(
            select(Project)
            .options(
                selectinload(Project.token_project)
                .selectinload(TokenProject.token)
            )
            .order_by(Project.created_at.desc())
        )
        return result.all()

    async def _enrich_with_chain_data(
        self, project: Project
    ) -> ProjectFundraisingDetail:
        offering_address = project.offering_address
        raised_amount = None
        soft_cap = None
        hard_cap = None

        if offering_address:
            try:
                service = OfferingService(offering_address)
                raised_raw = await asyncio.to_thread(service.total_raised)
                raised_amount = Decimal(raised_raw) / Decimal(10**6)

                soft_raw = await asyncio.to_thread(service.soft_cap)
                soft_cap = Decimal(soft_raw) / Decimal(10**6)

                hard_raw = await asyncio.to_thread(service.hard_cap)
                hard_cap = Decimal(hard_raw) / Decimal(10**6)
            except Exception:
                pass

        goal_amount = project.total_amount

        funding_percentage = None
        if goal_amount and goal_amount > 0 and raised_amount is not None:
            funding_percentage = float(raised_amount / goal_amount * 100)

        token_project = project.token_project
        total_supply = None
        available_supply = None
        tokens_sold = None

        if token_project:
            total_supply = token_project.total_supply
            available_supply = token_project.available_supply
            if total_supply is not None and available_supply is not None:
                tokens_sold = total_supply - available_supply

        inv_count, tx_count = await self._get_investment_stats(project.id)

        return ProjectFundraisingDetail(
            project_id=project.id,
            name=project.name,
            state=project.state,
            goal_amount=goal_amount,
            raised_amount=raised_amount,
            funding_percentage=funding_percentage,
            soft_cap=soft_cap,
            hard_cap=hard_cap,
            investor_count=inv_count,
            investment_tx_count=tx_count,
            tokens_sold=tokens_sold,
            total_supply=total_supply,
            offering_address=offering_address,
        )

    async def _get_investment_stats(self, project_id: UUID) -> tuple[int, int]:
        tx_count = await self.session.scalar(
            select(func.count(Transaction.id)).where(
                Transaction.project_id == project_id,
                Transaction.type == TransactionType.INVESTMENT,
            )
        )

        investor_count = await self.session.scalar(
            select(func.count(func.distinct(Transaction.wallet_id))).where(
                Transaction.project_id == project_id,
                Transaction.type == TransactionType.INVESTMENT,
            )
        )

        return (investor_count or 0), (tx_count or 0)

    async def _compute_summary(
        self, details: list[ProjectFundraisingDetail]
    ) -> FundraisingSummary:
        total_goal = None
        total_raised = None
        total_tokens_sold = None

        goal_values = [d.goal_amount for d in details if d.goal_amount is not None]
        if goal_values:
            total_goal = sum(goal_values, Decimal(0))

        raised_values = [
            d.raised_amount for d in details if d.raised_amount is not None
        ]
        if raised_values:
            total_raised = sum(raised_values, Decimal(0))

        sold_values = [d.tokens_sold for d in details if d.tokens_sold is not None]
        if sold_values:
            total_tokens_sold = sum(sold_values, Decimal(0))

        total_investors_row = await self.session.scalar(
            select(func.count(func.distinct(Transaction.wallet_id))).where(
                Transaction.type == TransactionType.INVESTMENT,
            )
        )

        total_tx = sum(d.investment_tx_count for d in details)

        return FundraisingSummary(
            total_projects=len(details),
            total_goal=total_goal,
            total_raised=total_raised,
            total_investors=total_investors_row or 0,
            total_tokens_sold=total_tokens_sold,
            total_investment_tx=total_tx,
        )
