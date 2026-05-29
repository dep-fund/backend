import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.role_service import RoleService
from app.services.permission_service import PermissionService
from app.models.role import Role
from app.models.permission import Permission
from app.models.permission_role import PermissionRole
from app.models.category import Category
from app.models.project import Project
from app.models.project_evaluation import ProjectEvaluation
from app.models.user import User
from app.schemas.role import RoleCreateRequest
from app.schemas.permission import (
    PermissionCreateRequest,
    PermissionRoleCreateRequest,
    PermissionRoleDeleteRequest,
    PermissionUpdateRequest,
)
from app.exceptions.role import RoleNotFound, RoleWithAssignedUsers
from app.exceptions.permission import (
    PermissionNotFound,
    PermissionRoleAlreadyAssigned,
    PermissionRoleNotFound,
    PermissionAlreadyExists,
)



# --- RoleService Tests ---

@pytest.mark.asyncio
async def test_role_create(mock_session):
    service = RoleService(mock_session)
    data = RoleCreateRequest(type="EDITOR")
    
    response = await service.create(data)
    
    assert response.type == "EDITOR"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_role_get_by_type_not_found(mock_session):
    mock_session.scalar.return_value = None
    service = RoleService(mock_session)
    
    with pytest.raises(RoleNotFound):
        await service.get_by_type("NON_EXISTENT")

@pytest.mark.asyncio
async def test_role_delete_success(mock_session):
    role = Role(id=uuid4(), type="TO_DELETE")
    role.users = []
    mock_session.scalar.return_value = role
    
    service = RoleService(mock_session)
    response = await service.delete("TO_DELETE")
    
    assert response["detail"] == "Role deleted successfully"
    mock_session.delete.assert_called_once_with(role)
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_role_delete_with_users(mock_session):
    role = Role(id=uuid4(), type="HAS_USERS")
    role.users = [MagicMock()] # Simulate assigned users
    mock_session.scalar.return_value = role
    
    service = RoleService(mock_session)
    
    with pytest.raises(RoleWithAssignedUsers):
        await service.delete("HAS_USERS")

# --- PermissionService Tests ---

@pytest.mark.asyncio
async def test_permission_create(mock_session):
    service = PermissionService(mock_session)
    data = PermissionCreateRequest(type="view_reports")
    
    response = await service.create(data)
    
    assert response.type == "view_reports"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_permission_assign_to_role_success(mock_session):
    role_id = uuid4()
    perm_id = uuid4()
    
    # Mocking check for role and permission existence
    mock_session.scalar.side_effect = [
        Role(id=role_id, type="ADMIN"), # RoleService.get_by_id
        Permission(id=perm_id, type="p1"), # PermissionService.get_by_id
        None # get_permission_role (not assigned yet)
    ]
    
    service = PermissionService(mock_session)
    data = PermissionRoleCreateRequest(role_id=role_id, permission_id=perm_id)
    
    response = await service.assign_to_role(data)
    
    assert response.role_id == role_id
    assert response.permission_id == perm_id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_permission_assign_to_role_already_assigned(mock_session):
    role_id = uuid4()
    perm_id = uuid4()
    
    mock_session.scalar.side_effect = [
        Role(id=role_id, type="ADMIN"),
        Permission(id=perm_id, type="p1"),
        PermissionRole(role_id=role_id, permission_id=perm_id) # Already exists
    ]
    
    service = PermissionService(mock_session)
    data = PermissionRoleCreateRequest(role_id=role_id, permission_id=perm_id)
    
    with pytest.raises(PermissionRoleAlreadyAssigned):
        await service.assign_to_role(data)

@pytest.mark.asyncio
async def test_permission_delete_assigned_success(mock_session):
    role_id = uuid4()
    perm_id = uuid4()
    rel = PermissionRole(role_id=role_id, permission_id=perm_id)
    
    mock_session.scalar.side_effect = [
        Role(id=role_id, type="ADMIN"),
        Permission(id=perm_id, type="p1"),
        rel
    ]
    
    service = PermissionService(mock_session)
    data = PermissionRoleDeleteRequest(role_id=role_id, permission_id=perm_id)
    
    response = await service.delete_assigned_permission_role(data)
    
    assert response["detail"] == "Permission from role deleted successfully"
    mock_session.delete.assert_called_once_with(rel)
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_permission_update_success(mock_session):
    perm_id = uuid4()
    perm = Permission(id=perm_id, type="old_type")
    
    # Mock result for get by id
    mock_result_get = MagicMock()
    mock_result_get.scalar_one_or_none.return_value = perm
    
    # Mock result for existence check
    mock_result_exists = MagicMock()
    mock_result_exists.scalar_one_or_none.return_value = None
    
    mock_session.execute.side_effect = [mock_result_get, mock_result_exists]
    
    service = PermissionService(mock_session)
    data = PermissionUpdateRequest(type="new_type")
    
    response = await service.update(perm_id, data)
    
    assert response.type == "new_type"
    assert perm.type == "new_type"
    mock_session.commit.assert_called_once()
