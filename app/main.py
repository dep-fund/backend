import logging
import time

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.exception_handlers import setup_exception_handlers
from app.core.logging_config import setup_logging


from app.routes.auth.oauth import router as oauth_router
from app.routes.health import router as health_router
from app.routes.auth.auth import router as auth_router
from app.routes.users.standard_user import router as users_router
from app.routes.users.admin_auth import router as admin_auth_router
from app.routes.users.admin_user import router as admin_router
from app.routes.role import router as admin_role
from app.routes.permission import router as admin_permission
from app.routes.projects.standard_user_project import (
    router as standard_user_project_router,
)
from app.routes.projects.admin_projects import router as admin_project_router
from app.routes.category.admin_category import router as admin_category_router
from app.routes.category.standard_user_category import (
    router as standard_user_category_router,
)
from app.routes.project_advance.admin_project_advance import (
    router as admin_project_advance,
)
from app.routes.project_advance.standard_user_project_advance import (
    router as standard_project_advance,
)
from app.routes.project_document.admin_project_document import (
    router as admin_project_document,
)
from app.routes.project_document.standard_user_project_document import (
    router as standard_project_document,
)
from app.routes.project_image.standard_user_project_image import (
    router as standard_project_image,
)
from app.routes.wallet import router as wallet_router
from app.routes.project_image.admin_project_image import router as admin_project_images
from app.routes.blockchain.marketplace import router as marketplace_router
from app.routes.token import router as token_router
from app.routes.blockchain.admin_dividends import router as admin_dividends
from app.routes.admin_reports import router as admin_reports_router
from app.routes.publication import router as publications_router
from app.routes.trades import router as trades_router
from app.routes.investment import router as investment_router
from app.routes.transaction import router as transaction_router

logger = logging.getLogger(__name__)
setup_logging()

app = FastAPI(
    title="DepFund API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "status": response.status_code,
            "duration_ms": round(elapsed * 1000, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )
    return response


setup_exception_handlers(app)

Instrumentator().instrument(app).expose(app, endpoint="/api/metrics")

api_v1 = APIRouter(prefix="/api")

# standard
api_v1.include_router(auth_router)
api_v1.include_router(oauth_router)
api_v1.include_router(users_router)
api_v1.include_router(standard_user_project_router)
api_v1.include_router(standard_user_category_router)
api_v1.include_router(standard_project_advance)
api_v1.include_router(standard_project_document)
api_v1.include_router(standard_project_image)
api_v1.include_router(wallet_router)
api_v1.include_router(marketplace_router)
api_v1.include_router(token_router)
api_v1.include_router(publications_router)
api_v1.include_router(trades_router)
api_v1.include_router(investment_router)

# admin
api_v1.include_router(admin_auth_router)
api_v1.include_router(admin_router)
api_v1.include_router(admin_role)
api_v1.include_router(admin_permission)
api_v1.include_router(admin_project_router)
api_v1.include_router(admin_category_router)
api_v1.include_router(admin_project_advance)
api_v1.include_router(admin_project_document)
api_v1.include_router(admin_project_images)

api_v1.include_router(health_router)
api_v1.include_router(admin_dividends)
api_v1.include_router(admin_reports_router)
api_v1.include_router(transaction_router)

app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(users_router)
app.include_router(standard_user_project_router)
app.include_router(standard_user_category_router)
app.include_router(standard_project_advance)
app.include_router(standard_project_document)
app.include_router(standard_project_image)
app.include_router(wallet_router)
app.include_router(marketplace_router)
app.include_router(token_router)
app.include_router(publications_router)
app.include_router(trades_router)
app.include_router(investment_router)

# admin
app.include_router(admin_auth_router)
app.include_router(admin_router)
app.include_router(admin_role)
app.include_router(admin_permission)
app.include_router(admin_project_router)
app.include_router(admin_category_router)
app.include_router(admin_project_advance)
app.include_router(admin_project_document)
app.include_router(admin_project_images)
app.include_router(admin_dividends)
app.include_router(admin_reports_router)
app.include_router(transaction_router)

app.include_router(api_v1)
