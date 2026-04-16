# Backend — DepFund

## Project structure

```
alembic/                → Database migrations
app/
├── core/               → Config, logging, security
├── routes/             → FastAPI routers
├── models/             → SQLAlchemy ORM models
├── schemas/            → Pydantic schemas
├── services/           → Business logic
└── db/                 → Session and engine setup
tests/                  → Mirrors routes/ and services/
```

---

## Local development

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Create a `.env` file in the project root based on the variables listed in the [environment variables](#environment-variables) section below.

> Never commit `.env` to the repository. It is already listed in `.gitignore`.

---

## Docker

```bash
docker compose up --build
```

Extra commands
```bash
docker compose down                  # stop
docker compose down -v               # stop + wipe database
docker compose logs -f backend       # tail logs
docker exec -it db psql -U postgres -d depfund
```

> The backend connects to Postgres on port `5432` internally.
> `POSTGRES_PORT` in `.env` is only the port exposed on your host machine.

---

## Manual server healtcheck

```bash
GET http://localhost:8000/health
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | Database host (`db` when using Docker) |
| `POSTGRES_PORT` | `5433` | Port exposed on the host machine |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_DB` | `depfund` | Database name |
| `SECRET_KEY` | — | Set to 1 automatically by Docker Compose |
| `LOG_SQL_QUERIES` | `0` | Set to 1 to echo SQL queries to stdout |