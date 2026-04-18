from app.exceptions.base import ExceptionHandler
from fastapi import status

class PermissionNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Permission not found."
    blocker = True

class PermissionRoleAlreadyAssigned(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "Permission already assigned to role."
    blocker = True
    
class PermissionRoleNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Permission role not found."
    blocker = True
    