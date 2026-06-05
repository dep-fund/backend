from app.exceptions.base import ExceptionHandler
from fastapi import status


class TokenNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Token not found."
    blocker = True


class TokenAlreadyExists(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "A token with that name or suffix already exists."
    blocker = True


class TokenProjectNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Token project relation not found."
    blocker = True


class TokenProjectAlreadyExists(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "This project already has a token associated."
    blocker = True


class InsufficientAvailableSupply(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Insufficient available supply for this operation."
    blocker = True
