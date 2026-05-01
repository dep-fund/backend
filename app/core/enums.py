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