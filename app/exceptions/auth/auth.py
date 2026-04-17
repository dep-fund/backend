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