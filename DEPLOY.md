# Guía de despliegue — DepFund en GCP

## Índice

1. [Prerrequisitos](#1-prerrequisitos)
2. [Configuración inicial de GCP](#2-configuración-inicial-de-gcp)
3. [Workload Identity Federation (GitHub ↔ GCP)](#3-workload-identity-federation-github--gcp)
4. [Arquitectura de red](#4-arquitectura-de-red)
5. [OpenTofu — Infraestructura](#5-opentofu--infraestructura)
6. [Frontend — Deploy a GCS](#6-frontend--deploy-a-gcs)
7. [GitHub Actions — Variables y Secrets](#7-github-actions--variables-y-secrets)
8. [Despliegue del backend](#8-despliegue-del-backend)
9. [Verificación](#9-verificación)
10. [Scripts de backup](#10-scripts-de-backup)
11. [Teardown](#11-teardown)
12. [Anexo: Comandos rápidos](#12-anexo-comandos-rápidos)
13. [Costos estimados](#13-costos-estimados)

---

## 1. Prerrequisitos

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| [OpenTofu](https://opentofu.org/docs/intro/install/) | ≥ 1.7 | `brew install opentofu` / `choco install opentofu` |
| [gcloud CLI](https://cloud.google.com/sdk/docs/install) | — | `brew install --cask google-cloud-sdk` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | — | `gcloud components install kubectl` |
| [GitHub CLI](https://cli.github.com/) (opcional) | — | `brew install gh` |

```bash
# Verificar instalaciones
tofu --version
gcloud --version
kubectl version --client
```

Además necesitás:
- Una cuenta de GCP con **facturación habilitada**
- Un repositorio en GitHub con el código del backend
- Archivos de secrets en `backend/secrets/` (ver `secrets/` directorio)
- Credenciales de **Google OAuth** (client id, client secret)
- **RPC URL** de tu red blockchain (Alchemy / Infura / propia)

---

## 2. Configuración inicial de GCP

### 2.1 Usar proyecto existente

```bash
gcloud config set project depfund-498022-d7
```

### 2.2 Habilitar APIs

```bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  compute.googleapis.com
```

### 2.3 Crear bucket para el estado de OpenTofu

El estado de OpenTofu se guarda en GCS para que el equipo pueda compartirlo.

```bash
BUCKET="depfund-tfstate-depfund-498022-d7"
gcloud storage buckets create gs://$BUCKET \
  --location=us-central1 \
  --uniform-bucket-level-access

echo "Bucket creado: gs://$BUCKET"
```

### 2.4 Verificar backend de OpenTofu

El archivo `infrastructure/backend.tf` ya está configurado con:

```hcl
backend "gcs" {
  bucket = "depfund-tfstate-depfund-498022-d7"
  prefix = "prod"
}
```

---

## 3. Workload Identity Federation (GitHub ↔ GCP)

Esto permite que GitHub Actions se autentique en GCP **sin keys de servicio**. Es más seguro y es requerido por el pipeline.

### 3.1 Crear el pool y provider

```bash
# Variables
PROJECT_ID=$(gcloud config get project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-provider"
REPO="dep-fund/backend"

# Crear pool de identidad
gcloud iam workload-identity-pools create $POOL_NAME \
  --project=$PROJECT_ID \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Obtener ID completo del pool
POOL_ID=$(gcloud iam workload-identity-pools describe $POOL_NAME \
  --project=$PROJECT_ID \
  --location="global" \
  --format="value(name)")

# Crear provider vinculado al repo
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
  --project=$PROJECT_ID \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == '$REPO'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 3.2 Crear Service Account para el deploy

```bash
SA_NAME="github-actions-deploy"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
  --project=$PROJECT_ID \
  --display-name="GitHub Actions Deploy"

# Roles necesarios para que GitHub Actions opere sobre GKE + GCS + Artifact Registry
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"
```

### 3.3 Vincular el SA al pool de identidad

```bash
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --project=$PROJECT_ID \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/$POOL_ID/attribute.repository/$REPO"
```

### 3.4 Guardar los valores para GitHub

Ejecutá estos comandos para obtener los valores que vas a configurar en GitHub:

```bash
echo "=== GitHub Repository Variables ==="
echo "GCP_PROJECT_ID:         $PROJECT_ID"
echo ""
echo "GCP_WIF_PROVIDER:       $(gcloud iam workload-identity-pools providers describe $PROVIDER_NAME \
  --project=$PROJECT_ID \
  --location=global \
  --workload-identity-pool=$POOL_NAME \
  --format='value(name)')"
echo "GCP_SERVICE_ACCOUNT:    $SA_EMAIL"
```

> Copiá estos tres valores. Los vas a necesitar en el [paso 5](#5-github-actions--variables-y-secrets).

> **Atención al repositorio:** El WIF se configuró para `dep-fund/backend`. Si tu repo en GitHub tiene otro nombre, ajustá la variable `REPO` en el paso 3.1.

---

## 4. Arquitectura de red

DepFund usa un **único Load Balancer HTTP** gestionado por OpenTofu que rutea según la URL:

| Ruta | Destino | Descripción |
|---|---|---|
| `/*` | Frontend GCS bucket | SPA pública (catch-all) |
| `/admin/*` | Backoffice GCS bucket | Panel admin SPA |
| `/api/*` | Backend GKE (vía NEG) | API REST |
| `/docs`, `/openapi.json`, `/redoc` | Backend GKE | Documentación Swagger |
| `/health` | Backend GKE | Health check |

### 4.1 Flujo de tráfico

```
Usuario → LB (IP estática global)
         ├── /*        → GCS bucket: prod-depfund-frontend
         ├── /admin/*  → GCS bucket: prod-depfund-backoffice
         └── /api/*    → GKE NEG → backend pods (puerto 8000)
```

> El **GKE Ingress anterior** fue reemplazado por este LB. Ver sección de migración.

---

## 5. OpenTofu — Infraestructura

### 5.1 Configurar variables

El archivo `infrastructure/environments/prod/terraform.tfvars` ya está configurado:

```hcl
gcp_project_id = "depfund-498022-d7"
gcp_region     = "us-central1"
environment    = "prod"
subnet_cidr    = "10.0.0.0/20"
```

### 5.2 Inicializar y aplicar

```bash
cd infrastructure/environments/prod

tofu init
tofu plan
tofu apply
```

Esto crea:
- VPC + subnet + NAT + firewall rules
- GKE Standard cluster (1 nodo spot `e2-small`, autoescala hasta 3)
- Artifact Registry repository (docker images)
- Cloud SQL (PostgreSQL 16, Private IP, backups automáticos, PITR 7 días)
- GCS bucket para backups
- **GCS buckets para frontend y backoffice** (públicos, static website)
- **HTTP Load Balancer** (reemplaza el GKE ingress, usa la IP estática existente)
- Service Accounts (cluster SA + backup SA + Cloud SQL)

El `apply` tarda **~8-12 minutos**.

> **Nota sobre el NEG:** El módulo LB necesita el `backend_neg_id` (self-link del NEG de GKE).
> El workflow de CI (`deploy.yml`) resuelve esto automáticamente: aplica los manifests de K8s,
> extrae el NEG ID del Service, lo escribe en `terraform.tfvars` y ejecuta `tofu apply`.
> Si es la primera vez, aplicá primero el plan sin el LB, deployá la app al GKE,
> y luego el workflow sincronizará el LB automáticamente.

### 5.3 Configurar el NEG de GKE (Network Endpoint Group)

El LB enruta al backend GKE mediante un NEG creado automáticamente por la annotation
`cloud.google.com/neg` en el Service. El workflow de CI lo resuelve automático.
Solo si necesitás hacerlo manual:

```bash
# 1. Aplicar el service con la annotation
kubectl apply -f kubernetes/service.yaml

# 2. Esperar a que GKE cree el NEG
sleep 15

# 3. Obtener el self_link del NEG
NEG_NAME=$(kubectl get svc depfund-backend -n depfund \
  -o jsonpath='{.metadata.annotations.cloud\.google\.com/neg-status}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['8000'])")
gcloud compute network-endpoint-groups describe "$NEG_NAME" \
  --region=us-central1 --format="value(selfLink)"
```

### 5.4 Outputs útiles

```bash
make infra-output
# lb_ip_address         → IP del LB
# frontend_bucket_name  → prod-depfund-frontend
# backoffice_bucket_name→ prod-depfund-backoffice
# cloudsql_private_ip   → IP privada de Cloud SQL
# cloudsql_db_name      → depfund
# cloudsql_db_user      → depfund_app
```

### 5.5 Conectarse al cluster

```bash
gcloud container clusters get-credentials prod-depfund-cluster \
  --region us-central1 \
  --project depfund-498022-d7
```

---

## 6. Frontend — Deploy a GCS

Cada frontend se buildea localmente y se sincroniza con su bucket GCS.
El bucket sirve como static website y el LB lo expone al público.

### 6.1 Manual (script)

```bash
# Frontend público
cd frontend
./scripts/deploy.sh

# Backoffice
cd backoffice
./scripts/deploy.sh
```

### 6.2 GitHub Actions (manual dispatch)

Desde GitHub → Actions → "Deploy Frontend to GCS" o "Deploy Backoffice to GCS",
elegí `workflow_dispatch` y el entorno.

**Variables de entorno requeridas en GitHub:**
- `FRONTEND_API_URL` — URL del backend para el frontend público (ej: `http://LB_IP/api`)
- `BACKOFFICE_API_URL` — URL del backend para el backoffice (ej: `http://LB_IP/api`)

> El prefijo `/api` se agrega automáticamente al `VITE_API_URL` de cada frontend.
> Ver [Arquitectura de red](#4-arquitectura-de-red).

---

## 7. GitHub Actions — Variables y Secrets

### 7.1 Repository Variables

En GitHub: **Settings → Secrets and variables → Actions → Variables**

| Variable | Valor |
|---|---|
| `GCP_PROJECT_ID` | `depfund-498022-d7` |
| `GCP_WIF_PROVIDER` | (lo obtuviste en 3.4) |
| `GCP_SERVICE_ACCOUNT` | `github-actions-deploy@depfund-498022-d7.iam.gserviceaccount.com` |
| `FRONTEND_API_URL` | `http://LB_IP/api` (IP del LB) |
| `BACKOFFICE_API_URL` | `http://LB_IP/api` (misma IP) |

### 7.2 Repository Secrets

En GitHub: **Settings → Secrets and variables → Actions → Secrets**

| Secret | Descripción |
|---|---|---|
| `POSTGRES_USER` | Usuario de la base de datos Cloud SQL |
| `POSTGRES_PASSWORD` | Password del usuario Cloud SQL |
| `POSTGRES_DB` | Nombre de la base de datos (`depfund`) |
| `SECRET_KEY` | JWT secret key (generar: `openssl rand -hex 32`) |
| `ADMIN_SECRET_KEY` | Admin guard key |
| `SENDER_PASSWORD` | Gmail App Password |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `DEPLOYER_PRIVATE_KEY` | Private key del deployer blockchain |

### 7.3 ConfigMap values

Antes del primer deploy, editá `kubernetes/configmap.yaml` con los valores correctos que no sean secretos:

| Key | Valor |
|---|---|
| `POSTGRES_HOST` | Se reemplaza automáticamente por `tofu output cloudsql_private_ip` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `depfund` |
| `RPC_URL` | URL de tu RPC (Infura/Alchemy) |
| `GOOGLE_REDIRECT_URI` | Se actualiza automáticamente en el deploy |

---

## 8. Despliegue del backend

### 8.1 Local (recomendado)

Un solo comando build + push + secrets + deploy:

```bash
make gke-all
```

O paso a paso:

```bash
make gke-connect        # conectar al cluster
make gke-build          # build + push a Artifact Registry
make gke-secrets        # crear/actualizar secrets desde ./secrets/
make gke-deploy         # aplicar manifests + rollout
```

El script `scripts/deploy.sh` hace lo mismo en un solo archivo.

### 8.2 Automático (GitHub Actions — opcional)

Cuando configures el Workload Identity Federation y los secrets en GitHub, al hacer push a `main` se dispara:

```
CI (test + lint) → Build & Push (Artifact Registry) → Deploy (GKE)
```

---

## 9. Verificación

### 9.1 Obtener IP del Load Balancer

```bash
make infra-output
# lb_ip_address = "X.X.X.X"
```

O directamente:

```bash
gcloud compute addresses describe prod-depfund-ingress-ip \
  --global --format="value(address)"
```

> La primera vez puede tardar **2-5 minutos** en que GCP provisione el Load Balancer.

### 9.2 Probar frontends

```bash
LB_IP=$(gcloud compute addresses describe prod-depfund-ingress-ip --global --format="value(address)")

# Frontend público
curl -sI http://$LB_IP/ | head -1
# → HTTP/1.1 200 OK

# Backoffice
curl -sI http://$LB_IP/admin/ | head -1
# → HTTP/1.1 200 OK

# API (health check)
curl -s http://$LB_IP/health
# → {"status":"ok"}
```

```bash
### 9.3 Testear health

```bash
LB_IP=$(gcloud compute addresses describe prod-depfund-ingress-ip --global --format="value(address)")
curl -sI http://$LB_IP/health
# → HTTP/1.1 200 OK
```

### 9.4 Logs del backend

```bash
kubectl logs -n depfund -l app=depfund-backend --tail=50 -f
```

### 9.5 Escalar manualmente (si hace falta)

```bash
kubectl scale deployment/depfund-backend -n depfund --replicas=3
```

---

## 10. Scripts de backup

### 10.1 Backup manual

```bash
# Obtener credenciales desde tofu
DB_IP=$(tofu -chdir=infrastructure/environments/prod output -raw cloudsql_private_ip)
DB_NAME=$(tofu -chdir=infrastructure/environments/prod output -raw cloudsql_db_name)
DB_USER=$(tofu -chdir=infrastructure/environments/prod output -raw cloudsql_db_user)
DB_PASS=$(tofu -chdir=infrastructure/environments/prod output -raw cloudsql_db_password)

# O ejecutar con el script que lee las credenciales del secret de K8s:
kubectl get secret depfund-secrets -n depfund \
  -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d
```

### 10.2 Backup automático (CronJob en K8s)

El CronJob en `kubernetes/backup-cronjob.yaml` corre automáticamente:
- **Schedule**: Domingo 3:00 AM UTC
- **Qué hace**: `pg_dump` → sube a GCS
- **Bucket**: `prod-depfund-backups`

Los dumps se borran del bucket después de **30 días** (lifecycle rule configurada en OpenTofu).

### 10.3 Restaurar desde backup

```bash
# Listar backups disponibles
gsutil ls gs://prod-depfund-backups/db/

# Descargar el más reciente
BUCKET="prod-depfund-backups"
LATEST=$(gsutil ls gs://$BUCKET/db/ | tail -1)
gsutil cp $LATEST ./restore.dump

# Restaurar (requiere acceso a la DB de destino)
pg_restore -h $TARGET_HOST -U $TARGET_USER -d $TARGET_DB \
  --no-owner --no-acl ./restore.dump
```

---

## 11. Teardown

Cuando termines las pruebas, destruí todo para no generar costos:

### 11.1 Destruir infraestructura

```bash
cd infrastructure/environments/prod
tofu destroy
```

Esto elimina: GKE cluster, VPC, NAT, firewall rules, Artifact Registry, Cloud SQL, GCS buckets.

> El bucket de backups se elimina **solo si está vacío**. Si tiene datos, vacialo primero o borralo manualmente desde la consola.

### 11.2 Eliminar proyecto (opcional, nuclear)

```bash
gcloud projects delete $(gcloud config get project)
```

---

## 12. Anexo: Comandos rápidos

```bash
# ─── Infra ──────────────────────────────────────
make infra-init          # tofu init
make infra-plan          # tofu plan
make infra-apply         # tofu apply
make infra-destroy       # tofu destroy
make infra-output        # tofu output (LB IP, buckets, etc.)

# ─── Backend (GKE) ──────────────────────────────
make gke-connect         # conectar al cluster
make gke-build           # build + push docker image
make gke-secrets         # inyectar secrets desde ./secrets/
make gke-deploy          # aplicar manifests + rollout
make gke-all             # ciclo completo: connect → build → secrets → deploy
make gke-logs            # logs del backend
make gke-logs-migrate    # logs de migración alembic

# ─── Frontend (GCS) ─────────────────────────────
cd frontend && ./scripts/deploy.sh     # deploy manual frontend
cd backoffice && ./scripts/deploy.sh   # deploy manual backoffice

# ─── K8s ────────────────────────────────────────
kubectl get pods -n depfund             # ver pods
kubectl delete namespace depfund        # borrar todo
kubectl get events -n depfund --sort-by=.lastTimestamp

# ─── LB ─────────────────────────────────────────
gcloud compute addresses describe prod-depfund-ingress-ip --global
make infra-output    # lb_ip_address

# ─── Logs ──────────────────────────────────────
kubectl logs -n depfund -l app=depfund-backend -f

# ─── Test ───────────────────────────────────────
pytest app/tests/ -v                              # tests locales
```

---

## 13. Costos estimados (GCP)

| Recurso | Costo aprox |
|---|---|
| GKE Standard (1 nodo spot `e2-small`) | ~$9/mes |
| Cloud NAT | ~$5/mes |
| Global HTTP LB + forwarding rule | ~$19/mes |
| Artifact Registry (1 imagen) | ~$0.50/mes |
| Cloud SQL (db-f1-micro, 20GB SSD) | ~$25/mes |
| GCS Backups + Frontend Buckets (pocos GB) | ~$1/mes |
| **Total estimado** | **~$60/mes** |

Si el cluster se usa **solo para pruebas/presentaciones**, hacé `tofu destroy` cuando no lo uses y solo pagás por el storage (GCS + Artifact Registry ≈ $1-2/mes).

---

> **Próximos pasos recomendados** (cuando hagan falta):
> - [x] Migrar frontends de Vercel a GCP (GCS + LB unificado)
> - [x] Migrar DB de Neon a Cloud SQL (ver `infrastructure/modules/cloudsql/`)
> - [ ] Agregar un dominio y TLS (Cloudflare o GCP-managed SSL)
> - [ ] Migrar secrets a GCP Secret Manager + External Secrets Operator
> - [ ] Migrar archivos de Cloudinary a GCS (ver `infrastructure/modules/uploads/`)
> - [ ] Agregar entorno `staging`
> - [ ] Implementar azul/verde (blue-green deployment)
