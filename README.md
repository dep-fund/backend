# Backend — DepFund

## Project Structure
alembic/ → Database migrations (version control for schema changes)
app/
├── core/ → Global configuration (environment variables, logging, security utilities)
├── routes/ → API route definitions (FastAPI routers/endpoints)
├── models/ → ORM models (SQLAlchemy)
├── schemas/ → Pydantic models for data validation and serialization
├── services/ → Business logic layer, reusable and independent from routes
└── db/ → Database configuration, session management, and base setup
tests/ → Test suite, organized to mirror routes and services