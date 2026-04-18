from pydantic import BaseModel, ConfigDict


class PermissionCreateRequest(BaseModel):
    type: str


class PermissionResponse(BaseModel):
    type: str
    
    model_config = ConfigDict(from_attributes=True)