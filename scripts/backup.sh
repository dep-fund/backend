#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# DepFund — Backup a GCS (uso manual o CronJob)
# ──────────────────────────────────────────────
# Uso: ./backup.sh
# Requiere: gcloud auth, psql, env vars cargadas

BUCKET="${BUCKET:-prod-depfund-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# ─── PostgreSQL dump ──────────────────────────
echo "[backup] Dumping PostgreSQL -> $TMPDIR/db_$TIMESTAMP.sql"
PGPASSWORD="${PGPASSWORD:?}" pg_dump \
  -h "${PGHOST:?}" -p "${PGPORT:-5432}" \
  -U "${PGUSER:?}" -d "${PGDB:?}" \
  --no-owner --no-acl \
  -F c \
  > "$TMPDIR/db_$TIMESTAMP.dump"

echo "[backup] Uploading DB dump to gs://$BUCKET/db/"
gsutil cp "$TMPDIR/db_$TIMESTAMP.dump" "gs://$BUCKET/db/"

# ─── Cloudinary backup (opcional) ─────────────
if [[ -n "${CLOUDINARY_CLOUD_NAME:-}" && -n "${CLOUDINARY_API_KEY:-}" && -n "${CLOUDINARY_API_SECRET:-}" ]]; then
  echo "[backup] Fetching Cloudinary resource list -> $TMPDIR/cloudinary_$TIMESTAMP.json"
  curl -s -u "${CLOUDINARY_API_KEY}:${CLOUDINARY_API_SECRET}" \
    "https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/resources/image?max_results=500" \
    > "$TMPDIR/cloudinary_$TIMESTAMP.json"

  echo "[backup] Uploading Cloudinary metadata to gs://$BUCKET/cloudinary/"
  gsutil cp "$TMPDIR/cloudinary_$TIMESTAMP.json" "gs://$BUCKET/cloudinary/"
fi

echo "[backup] Done — $TIMESTAMP"
