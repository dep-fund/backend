from fastapi import Request
from fastapi.responses import JSONResponse


class ExceptionHandler(Exception):
    code: int = 500
    message: str = "Internal server error"
    message_id: str | None = None
    blocker: bool = True

    def __init__(self, locale: str = "en", **kwargs):
        self.locale = locale
        self.extra = kwargs