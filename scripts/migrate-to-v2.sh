#!/usr/bin/env bash
# Migrerar produktions-databasen från v1.0 till v2.0.
#
# Vad scriptet gör:
#   1. Laddar MARIADB_ROOT_PASSWORD från .env
#   2. Verifierar att diaper_db-containern kör
#   3. Backup av hela databasen till ~/diaper_backups/backup-v1-<timestamp>.sql
#   4. Applicerar init_db/03-sleep-food.sql mot den körande databasen
#   5. Bygger om och startar om BARA app-containern (databasen rörs inte)
#   6. Printar verifieringskommandon
#
# Körs från repo-roten: ./scripts/migrate-to-v2.sh
# Idempotent: kan köras om (CREATE TABLE IF NOT EXISTS + ny backup-fil varje gång).

set -euo pipefail

DB_CONTAINER="diaper_db"
DB_NAME="diaper_counter"
BACKUP_DIR="$HOME/diaper_backups"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/backup-v1-$TIMESTAMP.sql"
MIGRATION_SQL="init_db/03-sleep-food.sql"

cd "$(dirname "$0")/.."

echo "==> Laddar .env"
if [[ ! -f .env ]]; then
    echo "FEL: .env saknas i repo-roten" >&2
    exit 1
fi
set -a
# shellcheck disable=SC1091
source .env
set +a

if [[ -z "${MARIADB_ROOT_PASSWORD:-}" ]]; then
    echo "FEL: MARIADB_ROOT_PASSWORD är inte satt i .env" >&2
    exit 1
fi

echo "==> Verifierar att $DB_CONTAINER kör"
if ! docker ps --format '{{.Names}}' | grep -qx "$DB_CONTAINER"; then
    echo "FEL: containern $DB_CONTAINER kör inte. Starta med: docker-compose up -d db" >&2
    exit 1
fi

echo "==> Verifierar att migrations-SQL finns"
if [[ ! -f "$MIGRATION_SQL" ]]; then
    echo "FEL: $MIGRATION_SQL saknas (är du på fel branch?)" >&2
    exit 1
fi

echo "==> Skapar backup-mapp $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo "==> Dumpar databasen till $BACKUP_FILE"
docker exec "$DB_CONTAINER" mariadb-dump \
    -uroot -p"$MARIADB_ROOT_PASSWORD" \
    --databases "$DB_NAME" \
    > "$BACKUP_FILE"

if [[ ! -s "$BACKUP_FILE" ]]; then
    echo "FEL: backupen är tom, avbryter innan migration" >&2
    exit 1
fi
echo "    Backup OK ($(du -h "$BACKUP_FILE" | cut -f1))"

echo "==> Applicerar $MIGRATION_SQL mot $DB_NAME"
docker exec -i "$DB_CONTAINER" mariadb \
    -uroot -p"$MARIADB_ROOT_PASSWORD" \
    "$DB_NAME" < "$MIGRATION_SQL"

echo "==> Bygger om och startar app-containern (databasen rörs inte)"
docker compose up -d --no-deps --build app

echo
echo "==> Klart. Verifiera med:"
echo "    curl -s http://localhost:2000/api/v1/changes/?limit=3   # gammal data kvar"
echo "    curl -s http://localhost:2000/api/v1/sleep/?hours=24    # []"
echo "    curl -s http://localhost:2000/api/v1/food/?hours=24     # []"
echo
echo "Backup ligger kvar på: $BACKUP_FILE"
