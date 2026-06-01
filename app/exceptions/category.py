from app.exceptions.base import ExceptionHandler
from fastapi import status

class CategoryNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Category not found."
    blocker = True
    
    
class CategoryHasProjects(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Cannot delete a category that is associated with at least one project."
    blocker = True