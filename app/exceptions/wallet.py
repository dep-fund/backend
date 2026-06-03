from app.exceptions.base import ExceptionHandler
from fastapi import status


class WalletNotFound(ExceptionHandler):
    code = status.HTTP_404_NOT_FOUND
    message = "Wallet not found."
    blocker = True


class WalletAlreadyExists(ExceptionHandler):
    code = status.HTTP_409_CONFLICT
    message = "This wallet address is already registered by another user."
    blocker = True


class WalletHasTransactions(ExceptionHandler):
    code = status.HTTP_400_BAD_REQUEST
    message = "Cannot delete a wallet that has at least one transaction associated."
    blocker = True


class WalletNotOwnedByUser(ExceptionHandler):
    code = status.HTTP_403_FORBIDDEN
    message = "This wallet does not belong to the current user."
    blocker = True
