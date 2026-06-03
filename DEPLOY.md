# Guía de despliegue — DepFund en GCP

## Índice

1. [Prerrequisitos](#1-prerrequisitos)
2. [Configuración inicial de GCP](#2-configuración-inicial-de-gcp)
3. [Workload Identity Federation (GitHub ↔ GCP)](#3-workload-identity-federation-github--gcp)
4. [OpenTofu — Infraestructura](#4-opentofu--infraestructura)
5. [GitHub Actions — Variables y Secrets](#5-github-actions--variables-y-secrets)
6. [Despliegue de la aplicación](#6-despliegue-de-la-aplicación)
7. [Verificación](#7-verificación)
8. [Scripts de backup](#8-scripts-de-backup)
9. [Teardown](#9-teardown)
10. [Anexo: Comandos rápidos](#10-anexo-comandos-rápidos)

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
- Credenciales de **Neon** (host, user, password, db name)
- Credenciales de **Cloudinary** (cloud name, api key, api secret)
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

## 4. OpenTofu — Infraestructura

### 4.1 Configurar variables

El archivo `infrastructure/environments/prod/terraform.tfvars` ya está configurado:

```hcl
gcp_project_id = "depfund-498022-d7"
gcp_region     = "us-central1"
environment    = "prod"
subnet_cidr    = "10.0.0.0/20"
```

### 4.2 Inicializar y aplicar

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
- GCS bucket para backups
- Service Accounts (cluster SA + backup SA)

El `apply` tarda **~5-8 minutos**.

### 4.3 Conectarse al cluster

```bash
gcloud container clusters get-credentials prod-depfund-cluster \
  --region us-central1 \
  --project depfund-498022-d7
```

---

## 5. GitHub Actions — Variables y Secrets

### 5.1 Repository Variables

En GitHub: **Settings → Secrets and variables → Actions → Variables**

| Variable | Valor |
|---|---|
| `GCP_PROJECT_ID` | `depfund-498022-d7` |
| `GCP_WIF_PROVIDER` | (lo obtuviste en 3.4) |
| `GCP_SERVICE_ACCOUNT` | `github-actions-deploy@depfund-498022-d7.iam.gserviceaccount.com` |

### 5.2 Repository Secrets

En GitHub: **Settings → Secrets and variables → Actions → Secrets**

| Secret | Descripción |
|---|---|
| `POSTGRES_USER` | `neondb_owner` |
| `POSTGRES_PASSWORD` | `npg_nk8gzJmIYei1` |
| `SECRET_KEY` | JWT secret key (generar: `openssl rand -hex 32`) |
| `ADMIN_SECRET_KEY` | Admin guard key |
| `SENDER_PASSWORD` | Gmail App Password |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `DEPLOYER_PRIVATE_KEY` | Private key del deployer blockchain |

### 5.3 ConfigMap values

Antes del primer deploy, editá `kubernetes/configmap.yaml` con los valores correctos que no sean secretos:

| Key | Valor |
|---|---|
| `POSTGRES_HOST` | `ep-square-hill-an7t5zyb-pooler.c-6.us-east-1.aws.neon.tech` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `neondb` |
| `RPC_URL` | URL de tu RPC (Infura/Alchemy) |
| `GOOGLE_REDIRECT_URI` | Se actualiza automáticamente en el deploy |

---

## 6. Despliegue de la aplicación

### 6.1 Local (recomendado)

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

### 6.2 Automático (GitHub Actions — opcional)

Cuando configures el Workload Identity Federation y los secrets en GitHub, al hacer push a `main` se dispara:

```
CI (test + lint) → Build & Push (Artifact Registry) → Deploy (GKE)
```

---

## 7. Verificación

### 7.1 Obtener IP del Load Balancer

```bash
kubectl get ingress depfund-ingress -n depfund

# Si querés solo la IP:
IP=$(kubectl get ingress depfund-ingress -n depfund \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $IP
```

> La primera vez puede tardar **2-5 minutos** en que GCP provisione el Load Balancer.

### 7.2 Testear health

```bash
curl -sI http://$IP/health
# → HTTP/1.1 200 OK
```

### 7.3 Logs del backend

```bash
kubectl logs -n depfund -l app=depfund-backend --tail=50 -f
```

### 7.4 Escalar manualmente (si hace falta)

```bash
kubectl scale deployment/depfund-backend -n depfund --replicas=3
```

---

## 8. Scripts de backup

### 8.1 Backup manual

```bash
# Configurar variables de entorno
export PGHOST="ep-xxx.us-east-2.aws.neon.tech"
export PGPORT="5432"
export PGUSER="..."
export PGPASSWORD="..."
export PGDB="depfund"
export BUCKET="prod-depfund-backups"
export CLOUDINARY_CLOUD_NAME="..."
export CLOUDINARY_API_KEY="..."
export CLOUDINARY_API_SECRET="..."

./scripts/backup.sh
```

### 8.2 Backup automático (CronJob en K8s)

El CronJob en `kubernetes/backup-cronjob.yaml` corre automáticamente:
- **Schedule**: Domingo 3:00 AM UTC
- **Qué hace**: `pg_dump` → sube a GCS
- **Bucket**: `prod-depfund-backups`

Los dumps se borran del bucket después de **30 días** (lifecycle rule configurada en OpenTofu).

### 8.3 Restaurar desde backup

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

## 9. Teardown

Cuando termines las pruebas, destruí todo para no generar costos:

### 9.1 Destruir infraestructura

```bash
cd infrastructure/environments/prod
tofu destroy
```

Esto elimina: GKE cluster, VPC, NAT, firewall rules, Artifact Registry, GCS bucket.

> El bucket de backups se elimina **solo si está vacío**. Si tiene datos, vacialo primero o borralo manualmente desde la consola.

### 9.2 Eliminar proyecto (opcional, nuclear)

```bash
gcloud projects delete $(gcloud config get project)
```

---

## 10. Anexo: Comandos rápidos

```bash
# ─── Infra ──────────────────────────────────────
make infra-init          # tofu init
make infra-plan          # tofu plan
make infra-apply         # tofu apply
make infra-destroy       # tofu destroy

# ─── K8s ────────────────────────────────────────
make k8s-apply           # kubectl apply -f kubernetes/
make k8s-delete          # borra namespace depfund

# ─── GKE ────────────────────────────────────────
gcloud container clusters get-credentials prod-depfund-cluster \
  --region us-central1 \
  --project depfund-prod

# ─── Logs ──────────────────────────────────────
kubectl logs -n depfund -l app=depfund-backend -f

# ─── Test ───────────────────────────────────────
pytest app/tests/ -v                              # tests locales
```

---

## Costos estimados (GCP)

| Recurso | Costo aprox |
|---|---|
| GKE Standard (1 nodo spot `e2-small`) | ~$9/mes |
| Cloud NAT | ~$5/mes |
| Artifact Registry (1 imagen) | ~$0.50/mes |
| GCS Backups (pocos GB) | ~$1/mes |
| **Total estimado** | **~$16/mes** |

Si el cluster se usa **solo para pruebas/presentaciones**, hacé `tofu destroy` cuando no lo uses y solo pagás por el storage (GCS + Artifact Registry ≈ $1-2/mes).

---

> **Próximos pasos recomendados** (cuando hagan falta):
> - [ ] Agregar un dominio y TLS (cert-manager + Cloud DNS)
> - [ ] Migrar secrets a GCP Secret Manager + External Secrets Operator
> - [ ] Agregar entorno `staging`
> - [ ] Implementar azul/verde (blue-green deployment)
