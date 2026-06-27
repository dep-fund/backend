from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProjectState, RiskLevel
from app.schemas.category import CategoryResponse


class DeveloperProjectSummary(BaseModel):
    id: UUID
    name: str
    suffix: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DeveloperResponse(BaseModel):
    id: UUID
    username: str
    name: str
    last_name: str
    email: str
    image: Optional[str] = None
    birthdate: date
    projects: List[DeveloperProjectSummary] = []

    model_config = ConfigDict(from_attributes=True)


class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    total_amount: Decimal
    ubication: str
    category_ids: Optional[List[UUID]] = None
    min_amount: Optional[Decimal] = None
    annual_expenses: Optional[Decimal] = None
    annual_gross_profit: Optional[Decimal] = None
    estimated_development_days: int = 180
    suffix: Optional[str] = Field(None, min_length=3, max_length=50)


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
    min_amount: Optional[Decimal] = None
    risk: Optional[RiskLevel] = None
    annual_expenses: Optional[Decimal] = None
    annual_gross_profit: Optional[Decimal] = None
    roi: Optional[Decimal] = None
    annual_benefits: Optional[Decimal] = None
    suffix: Optional[str] = None
    dividend_address: Optional[str] = None
    offering_address: Optional[str] = None
    developer: Optional[DeveloperResponse] = None

    model_config = ConfigDict(from_attributes=True)
