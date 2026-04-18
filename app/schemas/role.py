from pydantic import BaseModel, ConfigDict


class RoleCreateRequest(BaseModel):
    type: str

class RoleDeleteRequest(BaseModel):
    type: str


class RoleResponse(BaseModel):
    type: str
    
    model_config = ConfigDict(from_attributes=True)