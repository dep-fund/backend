from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import ProjectState


class ProjectFundraisingDetail(BaseModel):
    project_id: UUID
    name: str
    state: ProjectState
    goal_amount: Decimal | None
    raised_amount: Decimal | None
    funding_percentage: float | None
    soft_cap: Decimal | None = None
    hard_cap: Decimal | None = None
    investor_count: int
    investment_tx_count: int
    tokens_sold: Decimal | None = None
    total_supply: Decimal | None = None
    offering_address: str | None = None
    offering_fees: Decimal | None = None
    marketplace_fees: Decimal | None = None


class FundraisingSummary(BaseModel):
    total_projects: int
    total_goal: Decimal | None
    total_raised: Decimal | None
    total_investors: int
    total_tokens_sold: Decimal | None
    total_investment_tx: int
    total_offering_fees: Decimal | None = None
    total_marketplace_fees: Decimal | None = None
    total_revenue: Decimal | None = None


class FundraisingReport(BaseModel):
    summary: FundraisingSummary
    projects: list[ProjectFundraisingDetail]
