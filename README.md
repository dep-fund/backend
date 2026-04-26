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
├── tests/              → Unit and integration tests
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

## Testing

To run the test suite, ensure you have installed the testing dependencies (`pytest`, `pytest-asyncio`):
```bash
pytest app/tests/ -v
```

The project includes a GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs tests and database migrations automatically on pull requests and pushes to `main` and `develop`.

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | Database host (`db` when using Docker) |
| `POSTGRES_PORT` | `5433` | Port exposed on the host machine |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_DB` | `depfund` | Database name |
| `SECRET_KEY` | — | JWT Secret Key (set via secrets or .env) |
| `ADMIN_SECRET_KEY` | `develop` | Admin creation secret key |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP host for emails |
| `SMTP_PORT` | `587` | SMTP port (TLS) |
| `SENDER_EMAIL` | `depfund.soporte@gmail.com` | Email address for outgoing mails |
| `SENDER_PASSWORD` | — | Gmail App Password (16 characters) |
| `FRONTEND_URL` | `http://localhost:5173` | URL del frontend público |
| `BACKOFFICE_URL` | `http://localhost:5174` | URL del panel administrativo |
| `LOG_SQL_QUERIES` | `0` | Set to 1 to echo SQL queries to stdout |