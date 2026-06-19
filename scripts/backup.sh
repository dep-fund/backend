#!/usr/bin/env bash
set -euo pipefail

# DepFund — Backup a GCS (uso manual o CronJob)
# Uso: ./backup.sh
# Requiere: gcloud auth, psql, env vars cargadas

BUCKET="${BUCKET:-prod-depfund-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

ERRORS=""

notify() {
  local status="$1" msg="$2"
  if [ -n "${SENDER_PASSWORD:-}" ] && [ -n "${BACKUP_NOTIFY_EMAIL:-}" ]; then
    SENDER_EMAIL="${SENDER_EMAIL:-depfund.soporte@gmail.com}"
    curl --url 'smtps://smtp.gmail.com:465' --ssl-reqd \
      --mail-from "$SENDER_EMAIL" --mail-rcpt "$BACKUP_NOTIFY_EMAIL" \
      --user "$SENDER_EMAIL:$SENDER_PASSWORD" \
      -T <(printf "From: %s\nTo: %s\nSubject: [DepFund] Backup %s\n\n%s\n" \
        "$SENDER_EMAIL" "$BACKUP_NOTIFY_EMAIL" "$status" "$msg") || true
  fi
}

echo "============================================"
echo "  DepFund Backup — $TIMESTAMP"
echo "============================================"

# --- PostgreSQL dump ---
echo ""
echo "[backup] PostgreSQL dump -> db_$TIMESTAMP.dump"
PGPASSWORD="${PGPASSWORD:?}" pg_dump \
  -h "${PGHOST:?}" -p "${PGPORT:-5432}" \
  -U "${PGUSER:?}" -d "${PGDB:?}" \
  --no-owner --no-acl \
  -F c \
  > "$TMPDIR/db_$TIMESTAMP.dump" || ERRORS="${ERRORS}DB dump failed. "

DUMP_SIZE=$(du -sh "$TMPDIR/db_$TIMESTAMP.dump" | cut -f1)

echo "[backup] Uploading DB dump to gs://$BUCKET/db/"
gsutil cp "$TMPDIR/db_$TIMESTAMP.dump" "gs://$BUCKET/db/" || ERRORS="${ERRORS}DB upload failed. "

# --- Cloudinary assets backup ---
echo ""
if [ -n "${CLOUDINARY_CLOUD_NAME:-}" ] && [ -n "${CLOUDINARY_API_KEY:-}" ] && [ -n "${CLOUDINARY_API_SECRET:-}" ]; then
  echo "[backup] Cloudinary assets backup..."

  CLOUD_DIR="$TMPDIR/cloudinary"
  mkdir -p "$CLOUD_DIR"

  echo "  Listing resources..."
  curl -s -u "${CLOUDINARY_API_KEY}:${CLOUDINARY_API_SECRET}" \
    "https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/resources/image?max_results=500" \
    | jq -r '.resources[] | .secure_url' > "$TMPDIR/cloudinary_urls.txt" 2>/dev/null || \
    ERRORS="${ERRORS}Cloudinary listing failed. "

  if [ -s "$TMPDIR/cloudinary_urls.txt" ]; then
    TOTAL=$(wc -l < "$TMPDIR/cloudinary_urls.txt")
    echo "  Downloading $TOTAL images..."
    while IFS= read -r url; do
      filename="$(basename "${url%%\?*}")"
      curl -s -o "${CLOUD_DIR}/${filename}" "$url" || \
        ERRORS="${ERRORS}Failed to download $filename. "
    done < "$TMPDIR/cloudinary_urls.txt"
  fi

  echo "  Compressing and uploading..."
  tar -czf "$TMPDIR/cloudinary_$TIMESTAMP.tgz" -C "$CLOUD_DIR" .
  gsutil cp "$TMPDIR/cloudinary_$TIMESTAMP.tgz" "gs://$BUCKET/cloudinary/" || \
    ERRORS="${ERRORS}Cloudinary upload failed. "
else
  echo "[backup] Cloudinary not configured, skipping images"
fi

# --- Summary ---
echo ""
echo "============================================"
if [ -z "$ERRORS" ]; then
  echo "  Backup OK"
  notify "OK" "Backup completado.\nFecha: $TIMESTAMP\nDB: ${DUMP_SIZE}"
else
  echo "  Backup with ERRORS:"
  echo "  ${ERRORS}"
  notify "ERROR" "Backup con fallos:\n${ERRORS}"
fi
echo "============================================"
