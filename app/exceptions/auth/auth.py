from fastapi import status
from app.exceptions.base import ExceptionHandler


class InvalidCredentials(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid credentials."
    blocker = True


class UserBlocked(ExceptionHandler):
    code = status.HTTP_403_FORBIDDEN
    message = "User is blocked."
    blocker = True


class AccountNotActivated(ExceptionHandler):
    code = status.HTTP_403_FORBIDDEN
    message = "Account is not activated."
    blocker = True


class InvalidUserType(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid credentials."
    blocker = True

class PermissionDenied(ExceptionHandler):
    code = status.HTTP_403_FORBIDDEN
    message = "No tenés permiso."
    blocker = True



class PasswordResetTokenExpired(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Password reset token has expired."
    blocker = True


class PasswordResetTokenNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Password reset token not found."
    blocker = True


class PasswordResetTokenInvalid(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Password reset token is invalid."
    blocker = True
