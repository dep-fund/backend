from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import ExceptionHandler



def setup_exception_handlers(app: FastAPI):

    @app.exception_handler(ExceptionHandler)
    async def custom_exception_handler(request: Request, exc: ExceptionHandler):

        return JSONResponse(
            status_code=exc.code,
            content={
                "message": exc.message,
                "message_id": exc.message_id,
                "blocker": exc.blocker,
                "extra": exc.extra,
            },
        )