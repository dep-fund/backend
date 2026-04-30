from pydantic import BaseModel, ConfigDict
from uuid import UUID

class ProjectDocumentCreate(BaseModel):
    url: str

class ProjectDocumentResponse(BaseModel):
    project_id: UUID
    number: int
    url: str

    model_config = ConfigDict(from_attributes=True)