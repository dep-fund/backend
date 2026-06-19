#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# DepFund — Deploy local a GKE
# Uso: ./scripts/deploy.sh
# Requiere: gcloud autenticado, kubectl conectado al cluster
# ──────────────────────────────────────────────

PROJECT="depfund-498022-d7"
REGION="us-central1"
REGISTRY="${REGION}-docker.pkg.dev"
REPO="${REGISTRY}/${PROJECT}/depfund"
IMAGE="backend"
NAMESPACE="depfund"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TAG="${TIMESTAMP}"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "═══════════════════════════════════════════"
echo "  DepFund — Deploy local"
echo "  Tag: ${TAG}"
echo "═══════════════════════════════════════════"

# ─── 1. Build frontends (si existen los repos) ───
echo ""
if [ -d "${ROOT_DIR}/../frontend" ]; then
  echo "▸ Bulding frontend..."
  cd "${ROOT_DIR}/../frontend"
  npm ci && npm run build
  mkdir -p "${ROOT_DIR}/frontend-dist"
  cp -r dist/* "${ROOT_DIR}/frontend-dist/"
fi

if [ -d "${ROOT_DIR}/../backoffice" ]; then
  echo "▸ Building backoffice..."
  cd "${ROOT_DIR}/../backoffice"
  npm ci && npm run build
  mkdir -p "${ROOT_DIR}/backoffice-dist"
  cp -r dist/* "${ROOT_DIR}/backoffice-dist/"
fi

# ─── 2. Build backend image ────────────────────
echo ""
echo "▸ Build ${IMAGE}:${TAG}"
cd "${ROOT_DIR}"
docker build -t "${REPO}/${IMAGE}:${TAG}" -t "${REPO}/${IMAGE}:latest" "${ROOT_DIR}"

# ─── 3. Push ──────────────────────────────────
echo "▸ Push a Artifact Registry"
docker push "${REPO}/${IMAGE}:${TAG}"
docker push "${REPO}/${IMAGE}:latest"

# ─── 4. Namespace ─────────────────────────────
echo "▸ Namespace"
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# ─── 5. Secrets ──────────────────────────────
echo "▸ Secrets gestionados por GCP Secret Manager + ESO"
echo "  Para actualizar un secreto:"
echo "    gcloud secrets versions add depfund-<name> --data-file=secrets/<file>.txt"

# ─── 6. Apply manifests ──────────────────────
echo "▸ Apply manifests"
kubectl apply -f "${ROOT_DIR}/kubernetes/configmap.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/backup-sa.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/postgres-statefulset.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/secret-store.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/external-secret.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/service.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/hpa.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/backup-cronjob.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/ingress.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/certificate.yaml"

# ─── 7. Rollout ──────────────────────────────
echo "▸ Esperar rollout..."
kubectl rollout status deployment/depfund-backend -n "${NAMESPACE}" --timeout=5m

# ─── 8. IP ────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  Deploy completado ✅"
echo "  Ingress: https://depfund.34.58.61.129.sslip.io"
echo "  Para ver el estado: kubectl get pods -n depfund"
echo "═══════════════════════════════════════════"
