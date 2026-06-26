from fastapi import status

from app.exceptions.base import ExceptionHandler


class UsernameAlreadyTaken(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "Username already used."
    blocker = True


class EmailAlreadyRegistered(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "Email already used."
    blocker = True


class UserNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "User not found."
    blocker = True


class WrongCurrentPassword(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Wrong current password."
    blocker = True


class MinorAge(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "The user is minor age"
    blocker = True
