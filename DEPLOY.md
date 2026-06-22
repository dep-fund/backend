# Guia de despliegue -- DepFund en GCP

## Indice

1. [Prerrequisitos](#1-prerrequisitos)
2. [Configuracion inicial de GCP](#2-configuracion-inicial-de-gcp)
3. [Workload Identity Federation (GitHub GCP)](#3-workload-identity-federation-github--gcp)
4. [Arquitectura de red](#4-arquitectura-de-red)
5. [OpenTofu -- Infraestructura](#5-opentofu--infraestructura)
6. [Frontend y Backoffice -- Deploy a GKE](#6-frontend-y-backoffice--deploy-a-gke)
7. [GitHub Actions -- Variables y Secrets](#7-github-actions--variables-y-secrets)
8. [Despliegue del backend](#8-despliegue-del-backend)
9. [Verificacion](#9-verificacion)
10. [Backups](#10-backups)
11. [Teardown](#11-teardown)
12. [Anexo: Comandos rapidos](#12-anexo-comandos-rapidos)
13. [Costos estimados](#13-costos-estimados)

---

## 1. Prerrequisitos

| Herramienta | Version minima | Instalacion |
|---|---|---|
| [OpenTofu](https://opentofu.org/docs/intro/install/) | >= 1.7 | `brew install opentofu` / `choco install opentofu` |
| [gcloud CLI](https://cloud.google.com/sdk/docs/install) | -- | `brew install --cask google-cloud-sdk` |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | -- | `gcloud components install kubectl` |
| [GitHub CLI](https://cli.github.com/) (opcional) | -- | `brew install gh` |

```bash
# Verificar instalaciones
tofu --version
gcloud --version
kubectl version --client
```

Ademas necesitas:
- Una cuenta de GCP con facturacion habilitada
- Un repositorio en GitHub con el codigo del backend
- Archivos de secrets en `backend/secrets/` (ver `secrets/` directorio)
- Credenciales de Google OAuth (client id, client secret)
- RPC URL de tu red blockchain (Alchemy / Infura / propia)

---

## 2. Configuracion inicial de GCP

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

El archivo `infrastructure/backend.tf` ya esta configurado con:

```hcl
backend "gcs" {
  bucket = "depfund-tfstate-depfund-498022-d7"
  prefix = "prod"
}
```

---

## 3. Workload Identity Federation (GitHub GCP)

Esto permite que GitHub Actions se autentique en GCP sin keys de servicio.

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

Ejecuta estos comandos para obtener los valores que vas a configurar en GitHub:

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

> Copia estos tres valores. Los vas a necesitar en el [paso 7](#7-github-actions--variables-y-secrets).

> **Atencion al repositorio:** El WIF se configuro para `dep-fund/backend`. Si tu repo en GitHub tiene otro nombre, ajusta la variable `REPO` en el paso 3.1.

---

## 4. Arquitectura de red

DepFund usa un **nginx Ingress** dentro del cluster GKE que rutea segun la URL:

| Ruta | Destino | Descripcion |
|---|---|---|
| `/` | Frontend SPA (Deployment GKE, puerto 80) | SPA publica (catch-all) |
| `/admin` | Backoffice SPA (Deployment GKE, puerto 80) | Panel admin |
| `/api` | Backend API (Deployment GKE, puerto 8000) | API REST |
| `/docs`, `/openapi.json`, `/redoc` | Backend GKE | Documentacion Swagger |
| `/health` | Backend GKE | Health check |

### 4.1 Flujo de trafico

```
Usuario -> nginx Ingress (K8s, TLS via cert-manager)
           ├── /          -> depfund-frontend (Deployment GKE, puerto 80)
           ├── /admin     -> depfund-backoffice (Deployment GKE, puerto 80)
           └── /api       -> depfund-backend (Deployment GKE, puerto 8000)
                               -> postgres (StatefulSet GKE, puerto 5432)
```

### 4.2 TLS

El TLS se maneja con **cert-manager** + **Let's Encrypt** (ClusterIssuer `letsencrypt-prod`).
El certificado se emite para el dominio `depfund.34.58.61.129.sslip.io`.

Para instalar nginx-ingress y cert-manager por primera vez:

```bash
make gke-ingress-setup
```

Esto instala:
- `nginx-ingress` via Helm en namespace `nginx-ingress`
- `cert-manager` via Helm en namespace `cert-manager`
- ClusterIssuer `letsencrypt-prod`

---

## 5. OpenTofu -- Infraestructura

### 5.1 Configurar variables

El archivo `infrastructure/environments/prod/terraform.tfvars` ya esta configurado:

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
- GKE Standard cluster (1 nodo spot `e2-standard-2`, autoescala hasta 3)
- Artifact Registry repository (docker images)
- GCS bucket para backups (retencion: ARCHIVE a los 30 dias, DELETE a los 90)
- Service Accounts (cluster SA + backup SA)

El `apply` tarda **~8-12 minutos**.

### 5.3 Outputs utiles

```bash
make infra-output
# cluster_name         -> prod-depfund-cluster
# cluster_endpoint     -> IP del endpoint del cluster
# bucket_backups       -> prod-depfund-backups
# network_name         -> prod-depfund-vpc
```

### 5.4 Conectarse al cluster

```bash
gcloud container clusters get-credentials prod-depfund-cluster \
  --region us-central1 \
  --project depfund-498022-d7
```

---

## 6. Frontend y Backoffice -- Deploy a GKE

Ambos frontends se deployan como **Deployments** dentro del cluster GKE, servidos por el nginx Ingress.

### 6.1 Build de imagenes

Cada frontend tiene su propio `Dockerfile` que genera una imagen Nginx sirviendo el bundle estatico.

```bash
# Backend (incluye frontend-dist y backoffice-dist en el mismo repo)
cd backend
make gke-build
```

Si necesitas rebuildear solo un frontend:

```bash
# Frontend publico
cd frontend
docker build -t us-central1-docker.pkg.dev/depfund-498022-d7/depfund/frontend:latest .
docker push us-central1-docker.pkg.dev/depfund-498022-d7/depfund/frontend:latest

# Backoffice
cd backoffice
docker build -t us-central1-docker.pkg.dev/depfund-498022-d7/depfund/backoffice:latest .
docker push us-central1-docker.pkg.dev/depfund-498022-d7/depfund/backoffice:latest
```

### 6.2 Deploy de manifests

Los Deployments de frontend y backoffice estan en `kubernetes/`:

```bash
kubectl apply -f kubernetes/frontend-deployment.yaml
kubectl apply -f kubernetes/frontend-service.yaml
kubectl apply -f kubernetes/backoffice-deployment.yaml
kubectl apply -f kubernetes/backoffice-service.yaml
```

Tambien se deployan junto con el backend via `make gke-deploy` o ArgoCD.

### 6.3 ArgoCD (recomendado)

El deploy esta configurado via **ArgoCD** para sincronizacion automatica desde el repo `dep-fund/backend`, path `kubernetes/`, branch `main`.

Configuracion en `kubernetes/argo/application.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: depfund-backend
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/dep-fund/backend
    targetRevision: main
    path: kubernetes
  destination:
    server: https://kubernetes.default.svc
    namespace: depfund
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Al hacer push a `main`, ArgoCD sincroniza automaticamente.

---

## 7. GitHub Actions -- Variables y Secrets

### 7.1 Repository Variables

En GitHub: **Settings > Secrets and variables > Actions > Variables**

| Variable | Valor |
|---|---|
| `GCP_PROJECT_ID` | `depfund-498022-d7` |
| `GCP_WIF_PROVIDER` | (lo obtuviste en 3.4) |
| `GCP_SERVICE_ACCOUNT` | `github-actions-deploy@depfund-498022-d7.iam.gserviceaccount.com` |

### 7.2 Repository Secrets

En GitHub: **Settings > Secrets and variables > Actions > Secrets**

| Secret | Descripcion |
|---|---|
| `POSTGRES_USER` | Usuario de la base de datos |
| `POSTGRES_PASSWORD` | Password del usuario |
| `POSTGRES_DB` | Nombre de la base de datos (`depfund`) |
| `SECRET_KEY` | JWT secret key (generar: `openssl rand -hex 32`) |
| `ADMIN_SECRET_KEY` | Admin guard key |
| `SENDER_PASSWORD` | Gmail App Password |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `RPC_URL` | RPC endpoint para la blockchain |
| `DEPLOYER_PRIVATE_KEY` | Private key del deployer blockchain |

### 7.3 Secrets en GCP Secret Manager (via External Secrets Operator)

Los secrets se gestionan con **GCP Secret Manager** + **External Secrets Operator**.
El SecretStore (`kubernetes/secret-store.yaml`) apunta al proyecto GCP, y el ExternalSecret
(`kubernetes/external-secret.yaml`) mapea los secrets remotos a un Secret de K8s llamado
`depfund-secrets`.

Para subir/actualizar secrets desde los archivos locales en `secrets/`:

```bash
make gke-secrets-upload
```

Esto ejecuta `gcloud secrets versions add` para cada archivo en `backend/secrets/`.

---

## 8. Despliegue del backend

### 8.1 Manual (recomendado para devs)

Un solo comando build + push + secrets + deploy:

```bash
make gke-all
```

O paso a paso:

```bash
make gke-connect        # conectar al cluster
make gke-build          # build + push a Artifact Registry
make gke-secrets        # subir secrets a GCP Secret Manager
make gke-deploy         # aplicar manifests + rollout
```

`make gke-deploy` aplica los siguientes manifests en orden:
1. `configmap.yaml`
2. `backup-sa.yaml`
3. `postgres-statefulset.yaml`
4. `secret-store.yaml`
5. `external-secret.yaml`
6. `deployment.yaml`
7. `service.yaml`
8. `hpa.yaml`
9. `backup-cronjob.yaml`
10. `ingress.yaml`
11. `certificate.yaml`

### 8.2 Automatico (ArgoCD)

El deploy via ArgoCD aplica automaticamente los manifests del directorio `kubernetes/`
cada vez que hay un cambio en `main`. No requiere intervencion manual.

### 8.3 Base de datos

La base de datos corre como un **StatefulSet** de PostgreSQL 16 dentro del cluster GKE.
- PVC de 20Gi (storage class `standard-rwo`)
- Credenciales desde `depfund-secrets` (ExternalSecret)
- Health checks con `pg_isready`

La configuracion esta en `kubernetes/postgres-statefulset.yaml`.

#### Sincronizacion desde Neon (Testing)

En testing se usa **Neon** como base de datos. Periodicamente hay que sincronizar los
datos desde Neon al StatefulSet de Postgres en GKE:

```bash
# 1. Obtener dump desde Neon (consola o CLI de Neon)
# 2. Copiar el dump al pod de postgres
kubectl cp ./dump.sql depfund/postgres-0:/tmp/dump.sql

# 3. Restaurar en el StatefulSet
kubectl exec -n depfund postgres-0 -- psql -U postgres -d depfund -f /tmp/dump.sql
```

---

## 9. Verificacion

### 9.1 Obtener IP del nginx Ingress

```bash
kubectl get svc -n nginx-ingress nginx-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### 9.2 Probar endpoints

```bash
INGRESS_IP=$(kubectl get svc -n nginx-ingress nginx-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Frontend publico
curl -sI http://$INGRESS_IP/ | head -1
# -> HTTP/1.1 200 OK

# Backoffice
curl -sI http://$INGRESS_IP/admin | head -1
# -> HTTP/1.1 200 OK

# API (health check)
curl -s http://$INGRESS_IP/api/health
# -> {"status":"ok"}
```

### 9.3 Logs del backend

```bash
kubectl logs -n depfund -l app=depfund-backend --tail=50 -f
```

### 9.4 Escalar manualmente

```bash
kubectl scale deployment/depfund-backend -n depfund --replicas=3
```

---

## 10. Backups

### 10.1 Backup automatico (CronJob en K8s)

El CronJob en `kubernetes/backup-cronjob.yaml` corre automaticamente:
- **Schedule**: Domingo 3:00 AM UTC
- **Que hace**: `pg_dump` + sube a GCS + backup de Cloudinary
- **Bucket**: `prod-depfund-backups`
- **Notificacion**: Email a `depfund.soporte@gmail.com` via SMTP

Lifecycle del bucket:
- A los **30 dias** -> mueve a clase **ARCHIVE**
- A los **90 dias** -> **DELETE**

### 10.2 Backup manual desde el StatefulSet

```bash
# Obtener credenciales
kubectl get secret depfund-secrets -n depfund \
  -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d

# Hacer dump desde el pod
kubectl exec -n depfund postgres-0 -- pg_dump -U postgres -d depfund \
  --no-owner --no-acl -F c > ./backup_$(date +%Y%m%d).dump

# Subir a GCS
gsutil cp ./backup_*.dump gs://prod-depfund-backups/db/
```

### 10.3 Restaurar desde backup

```bash
# Listar backups disponibles
gsutil ls gs://prod-depfund-backups/db/

# Descargar el mas reciente
BUCKET="prod-depfund-backups"
LATEST=$(gsutil ls gs://$BUCKET/db/ | tail -1)
gsutil cp $LATEST ./restore.dump

# Copiar al pod
kubectl cp ./restore.dump depfund/postgres-0:/tmp/restore.dump

# Restaurar
kubectl exec -n depfund postgres-0 -- pg_restore -U postgres -d depfund \
  --no-owner --no-acl /tmp/restore.dump
```

### 10.4 Sincronizar desde Neon a GKE

Cuando se necesita actualizar el StatefulSet con datos frescos de Neon:

```bash
# 1. Exportar desde Neon (CLI o consola web de Neon)
# 2. Descargar el dump de Neon
# 3. Copiar al pod
kubectl cp ./neon_dump.sql depfund/postgres-0:/tmp/neon_dump.sql

# 4. Restaurar
kubectl exec -n depfund postgres-0 -- psql -U postgres -d depfund -f /tmp/neon_dump.sql
```

---

## 11. Teardown

Cuando termines las pruebas, destrui todo para no generar costos:

### 11.1 Destruir infraestructura

```bash
cd infrastructure/environments/prod
tofu destroy
```

Esto elimina: GKE cluster, VPC, NAT, firewall rules, Artifact Registry, GCS buckets.

> El bucket de backups se elimina solo si esta vacio. Si tiene datos, vacialo primero o borralo manualmente desde la consola.

### 11.2 Eliminar proyecto (opcional, nuclear)

```bash
gcloud projects delete $(gcloud config get project)
```

---

## 12. Anexo: Comandos rapidos

```bash
# --- Infra -------------------------------------------
make infra-init          # tofu init
make infra-plan          # tofu plan
make infra-apply         # tofu apply
make infra-destroy       # tofu destroy
make infra-output        # tofu output (cluster name, bucket, etc.)

# --- Backend (GKE) -----------------------------------
make gke-connect         # conectar al cluster
make gke-build           # build + push docker image
make gke-secrets         # inyectar secrets desde ./secrets/
make gke-deploy          # aplicar manifests + rollout
make gke-all             # ciclo completo: connect > build > secrets > deploy
make gke-logs            # logs del backend
make gke-logs-migrate    # logs de migracion alembic

# --- Instalacion unica de componentes ----------------
make gke-ingress-nginx   # instalar nginx-ingress via Helm
make gke-cert-manager    # instalar cert-manager via Helm
make gke-cluster-issuer  # aplicar ClusterIssuer de Let's Encrypt
make gke-ingress-setup   # todo lo anterior en un solo comando

# --- K8s ---------------------------------------------
kubectl get pods -n depfund             # ver pods
kubectl get svc -n nginx-ingress        # ver IP del Ingress
kubectl delete namespace depfund        # borrar todo
kubectl get events -n depfund --sort-by=.lastTimestamp

# --- Base de datos -----------------------------------
kubectl exec -n depfund postgres-0 -- psql -U postgres -d depfund

# --- Logs --------------------------------------------
kubectl logs -n depfund -l app=depfund-backend -f

# --- Test --------------------------------------------
pytest app/tests/ -v
```

---

## 13. Costos estimados (GCP)

| Recurso | Costo aprox |
|---|---|
| GKE Standard (1 nodo spot `e2-standard-2`) | ~$20/mes |
| Cloud NAT | ~$5/mes |
| Artifact Registry (1 imagen) | ~$0.50/mes |
| GCS Backups (pocos GB) | ~$0.50/mes |
| **Total estimado** | **~$26/mes** |

Si el cluster se usa solo para pruebas/presentaciones, hace `tofu destroy` cuando no lo uses y solo pagas por el storage (GCS + Artifact Registry ~$1-2/mes).

---

> **Proximos pasos recomendados** (cuando hagan falta):
> - [ ] Agregar un dominio real y migrar de `sslip.io`
> - [ ] Agregar entorno `staging`
> - [ ] Implementar azul/verde (blue-green deployment)
