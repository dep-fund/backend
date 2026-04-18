from fastapi import FastAPI
from app.core.exception_handlers import setup_exception_handlers
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.users.standard_user import router as users_router
from app.routes.users.admin_auth import router as admin_auth_router
from app.routes.users.admin_user import router as admin_router
from app.routes.role import router as admin_role
from app.routes.permission import router as admin_permission
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DepFund API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

setup_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_auth_router)
app.include_router(admin_router)
app.include_router(admin_role)
app.include_router(admin_permission)