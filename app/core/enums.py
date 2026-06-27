from enum import Enum


class UserType(str, Enum):
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"


class AuthProvider(str, Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"


class ProjectState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FileFolder(str, Enum):
    PROJECT_IMAGES = "projects/images"
    PROJECT_DOCUMENTS = "projects/documents"
    PROJECT_ADVANCES = "projects/advances"
    USER_AVATARS = "users/avatars"


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    DIVIDEND_DISTRIBUTION = "DIVIDEND_DISTRIBUTION"
    INVESTMENT = "INVESTMENT"


class PublicationStatus(str, Enum):
    active = "active"
    completed = "completed"
    canceled = "canceled"


class TradeStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"


class InvestmentSource(str, Enum):
    offering = "offering"
    marketplace = "marketplace"
