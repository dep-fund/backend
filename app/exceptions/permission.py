from app.exceptions.base import ExceptionHandler
from fastapi import status

class PermissionNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Permission not found."
    blocker = True