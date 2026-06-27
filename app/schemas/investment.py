from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import InvestmentSource


class InvestmentCreateRequest(BaseModel):
    token_quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(gt=0)
    tx_hash: str | None = None  # hash de la tx ya confirmada en MetaMask


class InvestmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    token_id: UUID
    token_quantity: Decimal
    unit_price: Decimal
    source: InvestmentSource
    is_active: bool
    tx_hash: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectInvestmentStats(BaseModel):
    raised_amount: Decimal
    investors_count: int
    progress_pct: Decimal