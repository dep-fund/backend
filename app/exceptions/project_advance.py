from app.exceptions.base import ExceptionHandler
from fastapi import status

class AdvanceNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Advance not found."
    blocker = True

class UnauthorizedAdvanceAccess(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized access advance."
    blocker = True
    