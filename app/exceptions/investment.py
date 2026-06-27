class InvestmentError(Exception):
    """Base exception for investment-related errors."""


class InvestmentNotFound(InvestmentError):
    pass


class ProjectNotInvestable(InvestmentError):
    """The project is not in a state that allows investment (must be APPROVED)."""


class InvalidInvestmentAmount(InvestmentError):
    """token_quantity or unit_price are invalid (<= 0)."""


class InvestmentExceedsHardCap(InvestmentError):
    """The investment would exceed the project's total_amount (hard cap)."""

class InsufficientHoldings(InvestmentError):
    """El usuario no tiene suficientes tokens activos de ese token para vender esa cantidad."""