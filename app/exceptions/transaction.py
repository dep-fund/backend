from app.exceptions.base import ExceptionHandler
from fastapi import status


class TransactionNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Transaction not found."
    blocker = True


class TransactionInvestmentRequiresProject(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "A transaction of type INVESTMENT must have a project associated."
    blocker = True


class TransactionProjectOnlyForInvestment(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Only transactions of type INVESTMENT can have a project associated."
    blocker = True
