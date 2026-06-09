from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProjectState, RiskLevel
from app.schemas.category import CategoryResponse


class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    total_amount: Decimal
    ubication: str

    min_amount: Decimal
    annual_expenses: Decimal
    annual_gross_profit: Decimal

    suffix: str = Field(..., min_length=3, max_length=50)

    estimated_development_days: int = 180

    category_ids: Optional[List[UUID]] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ubication: Optional[str] = None
    category_ids: Optional[List[UUID]] = None
    annual_expenses: Optional[Decimal] = None
    annual_gross_profit: Optional[Decimal] = None


class ProjectUpdateAdminRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    ubication: Optional[str] = None
    state: Optional[ProjectState] = None
    risk: Optional[RiskLevel] = None
    category_ids: Optional[List[UUID]] = None


class ProjectRejectRequest(BaseModel):
    reason: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str
    total_amount: Decimal
    state: ProjectState
    ubication: str
    user_id: UUID
    categories: List[CategoryResponse]
    created_at: datetime
    updated_at: datetime

    min_amount: Decimal
    risk: Optional[RiskLevel] = None
    annual_expenses: Decimal
    annual_gross_profit: Decimal
    roi: Optional[Decimal] = None
    annual_benefits: Optional[Decimal] = None

    suffix: str

    dividend_address: Optional[str] = None
    offering_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)