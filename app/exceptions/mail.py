from app.exceptions.base import ExceptionHandler
from fastapi import status

class MailServiceError(ExceptionHandler):
    code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Mail Service Error"
    blocker = False
    