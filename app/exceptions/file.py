from app.exceptions.base import ExceptionHandler
from fastapi import status


class FileExceedsLimit(ExceptionHandler):
    code = status.HTTP_413_CONTENT_TOO_LARGE
    message = "File exceeds the 12 MB limit."
    blocker = False


class FileTypeNotAllowed(ExceptionHandler):
    code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message = "File exceeds the 12 MB limit."
    blocker = False
