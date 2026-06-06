from uuid import UUID
from pydantic import BaseModel, ConfigDict


class RoleCreateRequest(BaseModel):
    type: str

class RoleDeleteRequest(BaseModel):
    type: str


class RoleResponse(BaseModel):
    id: UUID
    type: str
    
    model_config = ConfigDict(from_attributes=True)