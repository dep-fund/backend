from app.exceptions.base import ExceptionHandler
from fastapi import status

class RoleNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Role not found."
    blocker = True

class RoleWithAssignedUsers(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "Role already has assigned users."
    blocker = True