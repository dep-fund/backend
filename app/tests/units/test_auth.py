import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import BackgroundTasks

from app.services.auth.auth_service import AuthService
from app.services.users.standard_user_service import StandardUserService

from app.models.role import Role
from app.models.permission import Permission
from app.models.permission_role import PermissionRole
from app.models.project import Project
from app.models.project_evaluation import ProjectEvaluation
from app.models.user import User, StandardUser, AdminUser
from app.models.category import Category
from app.models.category_project import CategoryProject

from app.schemas.auth import ForgotPasswordRequest, LoginRequest, ResetPasswordRequest
from app.schemas.users.standard_user import StandardUserRegisterRequest
from app.exceptions.auth.auth import InvalidCredentials, PasswordResetTokenInvalid, PasswordResetTokenNotFound
from app.exceptions.users.user_exceptions import UsernameAlreadyTaken
from app.core.enums import UserType

from datetime import datetime


# --- Login Tests ---

@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.verify_password")
@patch("app.services.auth.auth_service.TokenService")
@pytest.mark.asyncio
async def test_login_success(MockTokenService, MockVerifyPassword, MockUserService, mock_session):
    # Setup
    mock_user = MagicMock()
    mock_user.id = uuid4()
    mock_user.username = "testuser"
    mock_user.password = "hashed_password"
    mock_user.type = UserType.STANDARD
    mock_user.blocked = False
    mock_user.activated = True
    mock_user.role.permissions = [MagicMock(type="p1")]
    
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_with_role_and_permissions = AsyncMock(return_value=mock_user)
    
    MockVerifyPassword.return_value = True
    MockTokenService.return_value.create_access_token.return_value = "access_token"
    
    auth_service = AuthService(mock_session)
    request = LoginRequest(identifier="testuser", password="password123")
    
    # Execute
    response = await auth_service.login(request)
    
    # Assert
    assert response.access_token == "access_token"
    MockVerifyPassword.assert_called_once_with("password123", "hashed_password")

@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.verify_password")
@pytest.mark.asyncio
async def test_login_invalid_credentials(MockVerifyPassword, MockUserService, mock_session):
    # Setup
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_with_role_and_permissions = AsyncMock(return_value=None)
    
    auth_service = AuthService(mock_session)
    request = LoginRequest(identifier="wronguser", password="password123")
    
    # Execute & Assert
    with pytest.raises(InvalidCredentials):
        await auth_service.login(request)

# --- Registration Tests ---

@patch("app.services.users.standard_user_service.UserService")
@patch("app.services.users.standard_user_service.RoleService")
@pytest.mark.asyncio
async def test_register_success(MockRoleService, MockUserService, mock_session):
    # Setup
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_by_username = AsyncMock(return_value=None)
    mock_user_service_instance.get_by_email = AsyncMock(return_value=None)
    
    mock_role = MagicMock()
    mock_role.id = uuid4()
    mock_role_service_instance = MockRoleService.return_value
    mock_role_service_instance.get_by_type = AsyncMock(return_value=mock_role)
    
    service = StandardUserService(mock_session)
    data = StandardUserRegisterRequest(
        username="newuser",
        email="new@example.com",
        password="Password123!",
        name="New",
        last_name="User",
        birthdate="1990-01-01"
    )
    
    # Execute
    response = await service.register(data)
    
    # Assert
    assert response.username == "newuser"
    assert mock_session.commit.called
    mock_session.add.assert_called()

@patch("app.services.users.standard_user_service.UserService")
@pytest.mark.asyncio
async def test_register_username_taken(MockUserService, mock_session):
    # Setup
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_by_username = AsyncMock(return_value=MagicMock())
    
    service = StandardUserService(mock_session)
    data = StandardUserRegisterRequest(
        username="takenuser",
        email="new@example.com",
        password="Password123!",
        name="New",
        last_name="User",
        birthdate="1990-01-01"
    )
    
    # Execute & Assert
    with pytest.raises(UsernameAlreadyTaken):
        await service.register(data)

# --- Forgot/Reset Password Tests (Existing) ---

@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.TokenService")
@patch("app.services.auth.auth_service.MailService")
@pytest.mark.asyncio
async def test_forgot_password_user_exists(MockMailService, MockTokenService, MockUserService, mock_session, background_tasks):
    mock_user = MagicMock()
    mock_user.id = uuid4()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.type = UserType.STANDARD
    
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_by_email = AsyncMock(return_value=mock_user)

    mock_token_service_instance = MockTokenService.return_value
    mock_token_service_instance.create_reset_token.return_value = "mocked_token"

    auth_service = AuthService(mock_session)
    request = ForgotPasswordRequest(email="test@example.com")
    
    # Execute
    response = await auth_service.forgot_password(request, background_tasks)
    
    # Assert
    assert response["message"] == "Si el correo electrónico está registrado, recibirás un enlace para restablecer tu contraseña."
    mock_token_service_instance.create_reset_token.assert_called_once()
    background_tasks.add_task.assert_called_once()
    
@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.TokenService")
@pytest.mark.asyncio
async def test_reset_password_success(MockTokenService, MockUserService, mock_session):
    # Setup user
    mock_user = MagicMock()
    mock_user.id = uuid4()
    
    # Setup token payload
    mock_token_service_instance = MockTokenService.return_value
    mock_token_service_instance.decode_token.return_value = {
        "token_kind": "reset",
        "user_id": str(mock_user.id),
        "sub": "testuser"
    }
    
    # Setup UserService
    mock_user_service_instance = MockUserService.return_value
    mock_user_service_instance.get_by_id = AsyncMock(return_value=mock_user)
    mock_user_service_instance.reset_password = AsyncMock()
    
    auth_service = AuthService(mock_session)
    request = ResetPasswordRequest(
        token="valid_token",
        new_password="newPassword123"
    )
    
    # Execute
    response = await auth_service.reset_password(request)
    
    # Assert
    assert response["message"] == "Contraseña actualizada correctamente."
    mock_user_service_instance.reset_password.assert_called_once()

@patch("app.services.auth.auth_service.TokenService")
@pytest.mark.asyncio
async def test_reset_password_invalid_token(MockTokenService, mock_session):
    mock_token_service_instance = MockTokenService.return_value
    mock_token_service_instance.decode_token.return_value = None # Invalid token
    
    auth_service = AuthService(mock_session)
    request = ResetPasswordRequest(
        token="invalid_token",
        new_password="newPassword123"
    )
    
    with pytest.raises(PasswordResetTokenInvalid):
        await auth_service.reset_password(request)
