import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import get_session, Base
from app.models.role import Role

import os

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER', 'test_user')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'test_password')}@"
    f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
    f"{os.getenv('POSTGRES_PORT', '5433')}/"
    f"{os.getenv('POSTGRES_DB', 'depfund_test')}"
)

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


# ---------------------------------------------------------------
# Override get_session → DB de testing
# ---------------------------------------------------------------
async def override_get_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise


app.dependency_overrides[get_session] = override_get_session


# ---------------------------------------------------------------
# Crea tablas al inicio y seedea roles — una sola vez por sesión
# ---------------------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seedea roles una sola vez
    async with TestingSessionLocal() as session:
        session.add(Role(type="ADMIN"))
        session.add(Role(type="STANDARD"))
        await session.commit()

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------
# Limpia todas las tablas EXCEPTO roles entre cada test
# ---------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    yield
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            if table.name != "ROLE":
                await conn.execute(table.delete())


# ---------------------------------------------------------------
# Cliente HTTP
# ---------------------------------------------------------------
@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


# ---------------------------------------------------------------
# Sesión directa a la DB
# ---------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session


# ---------------------------------------------------------------
# Standard user
# ---------------------------------------------------------------
@pytest_asyncio.fixture
async def standard_user_auth_headers(client: AsyncClient) -> dict:
    register_response = await client.post("/users/register", json={
        "username": "testuser",
        "name": "Standard",
        "last_name": "User",
        "email": "user@depfund.com",
        "password": "UserPassword123!",
    })
    assert register_response.status_code == 201, f"Register failed: {register_response.json()}"

    response = await client.post("/auth/login", json={
        "identifier": "user@depfund.com",
        "password": "UserPassword123!",
    })
    assert response.status_code == 200, f"Login failed: {response.json()}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------
# Admin user
# ---------------------------------------------------------------
@pytest_asyncio.fixture
async def admin_auth_headers(client: AsyncClient) -> dict:
    register_response = await client.post("/admin/users", json={
        "admin_secret_key": os.getenv("ADMIN_SECRET_KEY", "develop"),
        "username": "admintest",
        "name": "Admin",
        "last_name": "Test",
        "email": "admin@depfund.com",
        "password": "AdminPassword123!",
    })
    assert register_response.status_code == 201, f"Admin create failed: {register_response.json()}"

    response = await client.post("/admin/auth/login", json={
        "identifier": "admin@depfund.com",
        "password": "AdminPassword123!",
    })
    assert response.status_code == 200, f"Admin login failed: {response.json()}"

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
