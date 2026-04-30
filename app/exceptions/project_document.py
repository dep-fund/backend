from app.exceptions.base import ExceptionHandler
from fastapi import status

class DocumentNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Document not found."
    blocker = True

class UnauthorizedDocumentAccess(ExceptionHandler):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized access document."
    blocker = True
    