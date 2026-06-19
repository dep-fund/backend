#!/usr/bin/env bash
set -euo pipefail

# DepFund — Restore desde GCS
# Uso:
#   ./scripts/restore.sh                  # restore DB al target por defecto
#   ./scripts/restore.sh --list           # listar backups disponibles
#   ./scripts/restore.sh --dump-file gs://...  # restaurar un dump específico
#   ./scripts/restore.sh --db-host HOST   # restaurar contra otro host
#   ./scripts/restore.sh --cloudinary     # restaurar también Cloudinary assets

BUCKET="${BUCKET:-prod-depfund-backups}"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

DB_HOST="${PGHOST:-}"
DB_PORT="${PGPORT:-5432}"
DB_USER="${PGUSER:-}"
DB_PASS="${PGPASSWORD:-}"
DB_NAME="${PGDB:-}"
DUMP_FILE=""
DO_CLOUDINARY=false
MODE="restore"

usage() {
  echo "Uso: $0 [opciones]"
  echo ""
  echo "Opciones:"
  echo "  --list                           Listar backups disponibles"
  echo "  --dump-file gs://bucket/db/...   Restaurar un dump específico"
  echo "  --db-host HOST                   Target DB host (default: \$PGHOST)"
  echo "  --db-port PORT                   Target DB port (default: 5432)"
  echo "  --db-user USER                   Target DB user (default: \$PGUSER)"
  echo "  --db-pass PASS                   Target DB password (default: \$PGPASSWORD)"
  echo "  --db-name NAME                   Target DB name (default: \$PGDB)"
  echo "  --cloudinary                     Restaurar también Cloudinary assets"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --list) MODE="list"; shift ;;
    --dump-file) DUMP_FILE="$2"; shift 2 ;;
    --db-host) DB_HOST="$2"; shift 2 ;;
    --db-port) DB_PORT="$2"; shift 2 ;;
    --db-user) DB_USER="$2"; shift 2 ;;
    --db-pass) DB_PASS="$2"; shift 2 ;;
    --db-name) DB_NAME="$2"; shift 2 ;;
    --cloudinary) DO_CLOUDINARY=true; shift ;;
    *) usage ;;
  esac
done

list_backups() {
  echo "=== DB Backups disponibles ==="
  gsutil ls "gs://$BUCKET/db/" 2>/dev/null | sort -r || echo "  No hay backups de DB"

  echo ""
  echo "=== Cloudinary Backups disponibles ==="
  gsutil ls "gs://$BUCKET/cloudinary/" 2>/dev/null | sort -r || echo "  No hay backups de Cloudinary"
}

download_dump() {
  if [ -n "$DUMP_FILE" ]; then
    echo "Usando dump específico: $DUMP_FILE"
    gsutil cp "$DUMP_FILE" "$TMPDIR/restore.dump"
  else
    LATEST=$(gsutil ls "gs://$BUCKET/db/" 2>/dev/null | sort | tail -1)
    if [ -z "$LATEST" ]; then
      echo "ERROR: No hay backups de DB en gs://$BUCKET/db/"
      exit 1
    fi
    echo "Descargando el más reciente: $LATEST"
    gsutil cp "$LATEST" "$TMPDIR/restore.dump"
  fi
  echo "Dump descargado: $(du -sh "$TMPDIR/restore.dump" | cut -f1)"
}

restore_db() {
  if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASS" ] || [ -z "$DB_NAME" ]; then
    echo "ERROR: Faltan credenciales de DB. Usá las flags --db-host, --db-user, --db-pass, --db-name"
    exit 1
  fi

  echo "Restaurando dump en ${DB_HOST}:${DB_PORT}/${DB_NAME}..."
  echo "  DB: ${DB_NAME}"
  echo "  User: ${DB_USER}"
  echo ""

  PGPASSWORD="$DB_PASS" pg_restore \
    -h "$DB_HOST" -p "$DB_PORT" \
    -U "$DB_USER" -d "$DB_NAME" \
    --no-owner --no-acl \
    --verbose \
    "$TMPDIR/restore.dump"

  echo ""
  echo "Restore completado."
}

restore_cloudinary() {
  LATEST=$(gsutil ls "gs://$BUCKET/cloudinary/" 2>/dev/null | sort | tail -1)
  if [ -z "$LATEST" ]; then
    echo "No hay backups de Cloudinary"
    return
  fi

  echo "Descargando Cloudinary assets desde: $LATEST"
  gsutil cp "$LATEST" "$TMPDIR/cloudinary.tgz"
  tar -xzf "$TMPDIR/cloudinary.tgz" -C "$TMPDIR/cloudinary_out/"
  echo "Cloudinary assets extraídos en: $TMPDIR/cloudinary_out/"
  echo "Total de archivos: $(find "$TMPDIR/cloudinary_out/" -type f | wc -l)"
}

case "$MODE" in
  list)
    list_backups
    ;;
  restore)
    download_dump
    echo ""
    restore_db

    if [ "$DO_CLOUDINARY" = true ]; then
      echo ""
      restore_cloudinary
    fi

    echo ""
    echo "Restore finalizado."
    ;;
esac
