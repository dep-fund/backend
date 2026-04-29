from app.exceptions.base import ExceptionHandler
from fastapi import status

class CategoryNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Category not found."
    blocker = True