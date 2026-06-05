from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.exception_handlers import setup_exception_handlers
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

setup_exception_handlers(app)

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

app.include_router(health_router)
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
