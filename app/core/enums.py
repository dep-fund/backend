from enum import Enum


class UserType(str, Enum):
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"

class AuthProvider(str, Enum):
    LOCAL = "LOCAL"
    GOOGLE = "GOOGLE"