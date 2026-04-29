from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.models.project import ProjectState

class ProjectBase(BaseModel):
    name: str
    description: str
    total_amount: float = Field(gt=0)
    ubication: Optional[str] = None

class ProjectCreate(ProjectBase):
    user_id: UUID

class ProjectResponse(ProjectBase):
    id: int
    state: ProjectState
    created_at: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)