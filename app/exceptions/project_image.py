from app.exceptions.base import ExceptionHandler
from fastapi import status


class ImageNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Image not found."
    blocker = True


class UnauthorizedImageAccess(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized access image."
    blocker = True
