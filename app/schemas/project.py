from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import ProjectState,RiskLevel
from app.schemas.category import CategoryResponse

class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    total_amount: Decimal
    ubication: str
    category_ids: Optional[List[UUID]] = None
    min_amount: Optional[Decimal] = None
    annual_expenses: Optional[Decimal] = None
    annual_gross_profit: Optional[Decimal] = None
    suffix: Optional[str] = Field(None, min_length=3, max_length=50)


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[Decimal] = None
    ubication: Optional[str] = None
    state: Optional[ProjectState] = None
    category_ids: Optional[List[UUID]] = None
    min_amount: Optional[Decimal] = None
    risk: Optional[RiskLevel] = None
    annual_expenses: Optional[Decimal] = None
    annual_gross_profit: Optional[Decimal] = None
    suffix: Optional[str] = Field(None, min_length=3, max_length=50)


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

    model_config = ConfigDict(from_attributes=True)    
    
    
    
    
    
    
    