# Backend — DepFund

## Project structure

```
alembic/                → Database migrations
app/
├── core/               → Config, logging, security
├── routes/             → FastAPI routers
├── models/             → SQLAlchemy ORM models
├── schemas/            → Pydantic schemas
├── services/
│   └── blockchain/
│       ├── abis/       → Bundled contract artifacts (ABI + bytecode)
│       └── contracts/  → Contract service classes
├── tests/              → Unit and integration tests
└── db/                 → Session and engine setup
```

---

## Local development

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
pre-commit install
uvicorn app.main:app --reload --port 8000
```

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
pre-commit install
uvicorn app.main:app --reload --port 8000
```

Create a `.env` file in the project root based on the variables listed in the [environment variables](#environment-variables) section below.

> Never commit `.env` to the repository. It is already listed in `.gitignore`.

---

## Docker y Entornos

Creamos un `Makefile` para no tener que escribir los comandos largos de Docker. Existen dos configuraciones dependiendo de si estás en desarrollo o producción.

### Entorno de Desarrollo (Testing Local)
Incluye la base de datos, el backend con hot-reload, un nodo blockchain local (`anvil`) y despliega automáticamente los contratos de prueba.

Para levantar el entorno (y reconstruir si hay cambios):
```bash
make dev-up
```

Para apagar el entorno (asegura que `anvil` también se apague):
```bash
make dev-down
```

### Candidato a Deploy (Producción)
Solo levanta la base de datos y el backend. No incluye Anvil ni inicializa contratos. Se conecta a Sepolia como red remota.

```bash
make prod-up
make prod-down
```

### Comandos Útiles

```bash
make dev-down-v      # stop + wipe database local
make dev-logs        # tail logs del backend en local
make dev-db          # entrar a la base de datos por consola
make sync-abis       # sincronizar ABIs desde el repo de blockchain
```

> The backend connects to Postgres on port `5432` internally.
> `POSTGRES_PORT` in `.env` is only the port exposed on your host machine.

---

## Blockchain — Contract ABIs

El backend necesita los ABIs (y bytecode, para los contratos que despliega en runtime) de los smart contracts. Estos artifacts son generados por Foundry al compilar el repo `blockchain/` y se guardan versionados en `app/services/blockchain/abis/`.

### Por qué se commitean los ABIs

El backend es autónomo: no depende del repo de blockchain ni de ninguna ruta externa en runtime. Los artifacts en `abis/` son parte del backend igual que cualquier otro archivo de configuración.

### Contratos incluidos

| Contrato | Tipo de artifact | Motivo |
|---|---|---|
| `Offering` | Completo (ABI + bytecode) | El backend lo despliega en runtime al aprobar proyectos |
| `Dividends` | Completo (ABI + bytecode) | El backend lo despliega en runtime al aprobar proyectos |
| `DpfFactory` | Solo ABI | Ya desplegado en Sepolia, dirección fija en env vars |
| `Marketplace` | Solo ABI | Ya desplegado en Sepolia, dirección fija en env vars |

### Sincronizar artifacts

Cuando se modifica y recompila algún contrato, hay que re-sincronizar los artifacts al backend:

```bash
# Asumiendo estructura estándar del monorepo (backend/ y blockchain/ al mismo nivel)
cd backend/
make sync-abis

# Si el repo de blockchain está en otra ruta:
make sync-abis-custom BLOCKCHAIN_OUT=/ruta/a/blockchain/out
```

Luego commitear los cambios:
```bash
git add app/services/blockchain/abis/
git commit -m "chore: sync contract ABIs"
```

### Flujo completo al modificar un contrato

```
1. Modificar el contrato en blockchain
2. cd blockchain && forge build
3. cd backend && make sync-abis
4. git add app/services/blockchain/abis/ && git commit (para actualizar los abi cuando este todo testeado y desplegado en Sepolia)
5. make prod-up
```

---

## Manual server healthcheck

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

## Produccion (GKE + GCP)

### Arquitectura

```
nginx Ingress (K8s, TLS via cert-manager + Let's Encrypt)
  /          -> depfund-frontend (Deployment GKE, puerto 80)
  /admin     -> depfund-backoffice (Deployment GKE, puerto 80)
  /api       -> depfund-backend (Deployment GKE, puerto 8000)
                  -> postgres (StatefulSet GKE, puerto 5432)
```

La infraestructura se despliega via OpenTofu en GCP (proyecto `depfund-498022-d7`).
Los componentes se deployan como manifests de Kubernetes en el namespace `depfund`,
gestionados por ArgoCD desde `kubernetes/`.

### Sincronizacion Neon -> StatefulSet Postgres

En testing se usa **Neon** como base de datos. Para sincronizar datos desde Neon al
StatefulSet de Postgres en GKE:

```bash
# 1. Exportar dump desde Neon (consola o CLI)
# 2. Copiar al pod
kubectl cp ./neon_dump.sql depfund/postgres-0:/tmp/dump.sql

# 3. Restaurar
kubectl exec -n depfund postgres-0 -- psql -U postgres -d depfund -f /tmp/dump.sql
```

Ver `DEPLOY.md` para la guia completa de despliegue.

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_HOST` | `localhost` | Database host (`db` when using Docker, `postgres` en GKE) |
| `POSTGRES_PORT` | `5433` | Port exposed on the host machine |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `POSTGRES_DB` | `depfund` | Database name |
| `SECRET_KEY` | -- | JWT Secret Key (set via secrets or .env) |
| `ADMIN_SECRET_KEY` | `develop` | Admin creation secret key |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP host for emails |
| `SMTP_PORT` | `587` | SMTP port (TLS) |
| `SENDER_EMAIL` | `depfund.soporte@gmail.com` | Email address for outgoing mails |
| `SENDER_PASSWORD` | -- | Gmail App Password (16 characters) |
| `FRONTEND_URL` | `http://localhost:5173` | URL del frontend publico |
| `BACKOFFICE_URL` | `http://localhost:5174` | URL del panel administrativo |
| `LOG_SQL_QUERIES` | `0` | Set to 1 to echo SQL queries to stdout |
| `RPC_URL` | `http://127.0.0.1:8545` | RPC endpoint (Sepolia en prod, Anvil en dev) |
| `DEPLOYER_PRIVATE_KEY` | -- | Private key de la cuenta que firma transacciones |
| `GOOGLE_CLIENT_ID` | -- | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | -- | Google OAuth client secret |
| `FACTORY_ADDRESS` | -- | Direccion del contrato DpfFactory en Sepolia |
| `MARKETPLACE_ADDRESS` | -- | Direccion del contrato Marketplace en Sepolia |
| `USDC_ADDRESS` | -- | Direccion del contrato USDC en Sepolia |
| `TREASURY_ADDRESS` | -- | Direccion de la tesoreria del protocolo |
| `PLATFORM_ADDRESS` | -- | Direccion de la cuenta plataforma |
| `CLOUDINARY_CLOUD_NAME` | -- | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | -- | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | -- | Cloudinary API secret |