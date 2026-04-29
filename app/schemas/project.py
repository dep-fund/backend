from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.enums import ProjectState
from app.schemas.category import CategoryResponse


class ProjectCreateRequest(BaseModel):
    name: str
    description: str
    total_amount: Decimal
    ubication: str
    category_ids: Optional[List[UUID]] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[Decimal] = None
    ubication: Optional[str] = None
    state: Optional[ProjectState] = None
    category_ids: Optional[List[UUID]] = None


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

    model_config = ConfigDict(from_attributes=True)