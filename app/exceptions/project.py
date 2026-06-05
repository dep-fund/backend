from app.exceptions.base import ExceptionHandler
from fastapi import status


class ProjectNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Permission not found."
    blocker = True


class UnauthorizedProjectAccess(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized access project."
    blocker = True


class ProjectNotPending(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Project must be in pending state to be evaluated."
    blocker = True


class MissingMandatoryProjectInfo(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Project is missing mandatory information to be approved."
    blocker = True


class ProjectNameAlreadyExists(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "A project with that name already exists."
    blocker = True


class ProjectSuffixAlreadyExists(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "A project with that suffix already exists."
    blocker = True
