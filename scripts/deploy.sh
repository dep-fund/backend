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

# ─── 1. Build ─────────────────────────────────
echo ""
echo "▸ Build ${IMAGE}:${TAG}"
docker build -t "${REPO}/${IMAGE}:${TAG}" -t "${REPO}/${IMAGE}:latest" "${ROOT_DIR}"

# ─── 2. Push ──────────────────────────────────
echo "▸ Push a Artifact Registry"
docker push "${REPO}/${IMAGE}:${TAG}"
docker push "${REPO}/${IMAGE}:latest"

# ─── 3. Actualizar deployment.yaml ────────────
echo "▸ Actualizar imagen en el manifest"
sed -i "s|image:.*${REPO}/${IMAGE}:.*|image: ${REPO}/${IMAGE}:${TAG}|" "${ROOT_DIR}/kubernetes/deployment.yaml"
sed -i "s|image:.*${REPO}/${IMAGE}:.*|image: ${REPO}/${IMAGE}:${TAG}|" "${ROOT_DIR}/kubernetes/deployment.yaml"

# ─── 4. Namespace ─────────────────────────────
echo "▸ Namespace"
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# ─── 5. Secrets ──────────────────────────────
echo "▸ Secrets desde ./secrets/"
SECRETS_DIR="${ROOT_DIR}/secrets"
if [ -d "${SECRETS_DIR}" ]; then
  kubectl create secret generic depfund-secrets -n "${NAMESPACE}" \
    --from-literal=POSTGRES_USER=neondb_owner \
    --from-literal=POSTGRES_PASSWORD=npg_nk8gzJmIYei1 \
    --from-literal=POSTGRES_DB=neondb \
    --from-literal=SECRET_KEY="$(cat "${SECRETS_DIR}/secret_key.txt")" \
    --from-literal=ADMIN_SECRET_KEY="$(cat "${SECRETS_DIR}/admin_secret_key.txt")" \
    --from-literal=SENDER_PASSWORD="$(cat "${SECRETS_DIR}/sender_password.txt")" \
    --from-literal=GOOGLE_CLIENT_ID="$(cat "${SECRETS_DIR}/google_client_id.txt")" \
    --from-literal=GOOGLE_CLIENT_SECRET="$(cat "${SECRETS_DIR}/google_client_secret.txt")" \
    --from-literal=CLOUDINARY_CLOUD_NAME="$(cat "${SECRETS_DIR}/cloudinary_cloud_name.txt")" \
    --from-literal=CLOUDINARY_API_KEY="$(cat "${SECRETS_DIR}/cloudinary_api_key.txt")" \
    --from-literal=CLOUDINARY_API_SECRET="$(cat "${SECRETS_DIR}/cloudinary_api_secret.txt")" \
    --from-literal=DEPLOYER_PRIVATE_KEY="$(cat "${SECRETS_DIR}/deployer_private_key.txt")" \
    --dry-run=client -o yaml | kubectl apply -f -
else
  echo "  ⚠️  Directorio ./secrets/ no encontrado. Secrets no actualizados."
fi

# ─── 6. Apply manifests ──────────────────────
echo "▸ Apply manifests"
kubectl apply -f "${ROOT_DIR}/kubernetes/configmap.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/deployment.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/service.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/ingress.yaml"
kubectl apply -f "${ROOT_DIR}/kubernetes/hpa.yaml"

# ─── 7. Rollout ──────────────────────────────
echo "▸ Esperar rollout..."
kubectl rollout status deployment/depfund-backend -n "${NAMESPACE}" --timeout=5m

# ─── 8. IP ────────────────────────────────────
IP=$(kubectl get ingress depfund-ingress -n "${NAMESPACE}" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pendiente")
echo ""
echo "═══════════════════════════════════════════"
echo "  Deploy completado ✅"
echo "  IP: ${IP}"
echo "  Health: curl -s http://${IP}/health"
echo "═══════════════════════════════════════════"
