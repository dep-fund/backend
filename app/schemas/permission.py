from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PermissionCreateRequest(BaseModel):
    type: str


class PermissionResponse(BaseModel):
    type: str
    
    model_config = ConfigDict(from_attributes=True)


class PermissionRoleCreateRequest(BaseModel):
    role_id: UUID
    permission_id: UUID


class PermissionRoleResponse(BaseModel):
    role_id: UUID
    permission_id: UUID