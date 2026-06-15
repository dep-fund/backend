.PHONY: dev-up dev-down dev-logs dev-db \
        infra-init infra-plan infra-apply infra-destroy \
        gke-connect gke-build gke-secrets gke-deploy gke-all gke-logs gke-logs-migrate \
        gke-ingress-nginx gke-cert-manager gke-cluster-issuer gke-ingress-setup

# ─────────────────────────────────────────────
# Entorno de Desarrollo (Docker Compose)
# ─────────────────────────────────────────────

dev-up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-down-v:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

dev-logs:
	docker compose logs -f backend

dev-logs-deployer:
	docker compose logs -f deployer

dev-logs-anvil:
	docker compose logs -f anvil

dev-db:
	docker exec -it db psql -U postgres -d depfund


# ─────────────────────────────────────────────
# Infraestructura GCP (OpenTofu)
# ─────────────────────────────────────────────

TOFU_ENV := prod
TOFU_DIR := infrastructure/environments/${TOFU_ENV}

infra-init:
	cd ${TOFU_DIR} && tofu init

infra-plan:
	cd ${TOFU_DIR} && tofu plan

infra-apply:
	cd ${TOFU_DIR} && tofu apply

infra-destroy:
	cd ${TOFU_DIR} && tofu destroy

infra-output:
	cd ${TOFU_DIR} && tofu output


# ─────────────────────────────────────────────
# Variables GCP/GKE
# ─────────────────────────────────────────────

PROJECT    := depfund-498022-d7
REGION     := us-central1
REGISTRY   := ${REGION}-docker.pkg.dev
REPO       := ${REGISTRY}/${PROJECT}/depfund
IMAGE      := backend
NAMESPACE  := depfund
CLUSTER    := prod-depfund-cluster

# ─────────────────────────────────────────────
# Conexión al cluster
# ─────────────────────────────────────────────

gke-connect:
	gcloud container clusters get-credentials ${CLUSTER} \
		--zone us-central1-a \
		--project ${PROJECT}


# ─────────────────────────────────────────────
# Build + Push manual
# ─────────────────────────────────────────────

gke-build:
	TAG=$$(date +%Y%m%d_%H%M%S); \
	docker build -t ${REPO}/${IMAGE}:$$TAG -t ${REPO}/${IMAGE}:latest .; \
	docker push ${REPO}/${IMAGE}:$$TAG; \
	docker push ${REPO}/${IMAGE}:latest; \
	echo "Imagen: ${REPO}/${IMAGE}:$$TAG"


# ─────────────────────────────────────────────
# Secrets desde ./secrets/ (sin tocar GitHub)
# ─────────────────────────────────────────────

gke-secrets:
	kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -; \
	S=secrets; \
	kubectl create secret generic depfund-secrets -n ${NAMESPACE} \
		--from-literal=POSTGRES_USER="$$(cat $$S/postgres_user.txt)" \
		--from-literal=POSTGRES_PASSWORD="$$(cat $$S/postgres_password.txt)" \
		--from-literal=POSTGRES_DB="$$(cat $$S/postgres_db.txt)" \
		--from-literal=SECRET_KEY="$$(cat $$S/secret_key.txt)" \
		--from-literal=ADMIN_SECRET_KEY="$$(cat $$S/admin_secret_key.txt)" \
		--from-literal=SENDER_PASSWORD="$$(cat $$S/sender_password.txt)" \
		--from-literal=GOOGLE_CLIENT_ID="$$(cat $$S/google_client_id.txt)" \
		--from-literal=GOOGLE_CLIENT_SECRET="$$(cat $$S/google_client_secret.txt)" \
		--from-literal=CLOUDINARY_CLOUD_NAME="$$(cat $$S/cloudinary_cloud_name.txt)" \
		--from-literal=CLOUDINARY_API_KEY="$$(cat $$S/cloudinary_api_key.txt)" \
		--from-literal=CLOUDINARY_API_SECRET="$$(cat $$S/cloudinary_api_secret.txt)" \
		--from-literal=DEPLOYER_PRIVATE_KEY="$$(cat $$S/deployer_private_key.txt)" \
		--dry-run=client -o yaml | kubectl apply -f -


# ─────────────────────────────────────────────
# Deploy manifests al cluster
# ─────────────────────────────────────────────

gke-deploy:
	kubectl apply -f kubernetes/configmap.yaml; \
	kubectl apply -f kubernetes/backup-sa.yaml; \
	kubectl apply -f kubernetes/deployment.yaml; \
	kubectl apply -f kubernetes/service.yaml; \
	kubectl apply -f kubernetes/hpa.yaml; \
	kubectl apply -f kubernetes/backup-cronjob.yaml; \
	kubectl apply -f kubernetes/ingress.yaml; \
	kubectl apply -f kubernetes/certificate.yaml; \
	kubectl rollout status deployment/depfund-backend -n ${NAMESPACE} --timeout=5m; \
	echo "Ingress: https://depfund.34.58.61.129.sslip.io  (reemplazar 34.58.61.129 con la IP del nginx-ingress)"


# ─────────────────────────────────────────────
# Instalación única de nginx-ingress + cert-manager
# ─────────────────────────────────────────────

gke-ingress-nginx:
	helm repo add nginx-stable https://helm.nginx.com/stable || true; \
	helm repo update; \
	helm upgrade --install nginx-ingress nginx-stable/nginx-ingress \
		--namespace nginx-ingress --create-namespace

gke-cert-manager:
	helm repo add jetstack https://charts.jetstack.io || true; \
	helm repo update; \
	helm upgrade --install cert-manager jetstack/cert-manager \
		--namespace cert-manager --create-namespace \
		--set installCRDs=true; \
	kubectl wait --for=condition=Ready pods -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=120s

gke-cluster-issuer:
	kubectl apply -f kubernetes/cluster-issuer.yaml

gke-ingress-setup: gke-ingress-nginx gke-cert-manager gke-cluster-issuer
	@echo "✅ nginx-ingress + cert-manager instalados."

# ─────────────────────────────────────────────
# Full ciclo: build → push → secrets → deploy
# ─────────────────────────────────────────────

gke-all: gke-connect gke-build gke-secrets gke-deploy


# ─────────────────────────────────────────────
# Logs
# ─────────────────────────────────────────────

gke-logs:
	kubectl logs -n ${NAMESPACE} -l app=depfund-backend -f

gke-logs-migrate:
	kubectl logs -n ${NAMESPACE} -l app=depfund-backend --tail=-1 2>/dev/null | grep -A5 "alembic" || echo "No hay logs de migración"


# ─────────────────────────────────────────────
# Teardown
# ─────────────────────────────────────────────

k8s-delete:
	kubectl delete namespace ${NAMESPACE} --ignore-not-found
