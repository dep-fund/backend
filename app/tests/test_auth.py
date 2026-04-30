import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import BackgroundTasks

from app.services.auth.auth_service import AuthService
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.exceptions.auth.auth import PasswordResetTokenInvalid, PasswordResetTokenNotFound


@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def background_tasks():
    return MagicMock(spec=BackgroundTasks)

@pytest.mark.asyncio
@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.TokenService")
@patch("app.services.auth.auth_service.MailService")
async def test_forgot_password_user_exists(MockMailService, MockTokenService, MockUserService, mock_session, background_tasks):
    mock_user = MagicMock()
    mock_user.id = uuid4()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    mock_user.type = MagicMock()
    mock_user.type.value = "STANDARD"
    
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
    
    # Verify token was created with right data
    mock_token_service_instance.create_reset_token.assert_called_once_with(
        data={
            "sub": "testuser",
            "user_id": str(mock_user.id),
            "token_kind": "reset"
        }
    )
    
    # Verify email was scheduled
    background_tasks.add_task.assert_called_once()
    
@pytest.mark.asyncio
@patch("app.services.auth.auth_service.UserService")
@patch("app.services.auth.auth_service.TokenService")
async def test_reset_password_success(MockTokenService, MockUserService, mock_session):
    # Setup user
    mock_user = MagicMock()
    mock_user.id = uuid4()
    mock_user.email = "test@example.com"
    mock_user.username = "testuser"
    
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
    mock_user_service_instance.reset_password.assert_called_once_with(mock_user.id, "newPassword123")

@pytest.mark.asyncio
@patch("app.services.auth.auth_service.TokenService")
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
