from enum import Enum


class UserType(str, Enum):
    STANDARD = "STANDARD"
    ADMIN = "ADMIN"