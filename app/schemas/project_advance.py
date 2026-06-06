from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class ProjectAdvanceCreate(BaseModel):
    description: str
    url: Optional[str] = None

class ProjectAdvanceResponse(BaseModel):
    project_id: UUID
    number: int
    description: str
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)