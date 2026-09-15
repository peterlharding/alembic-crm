#!/usr/bin/env bash
#
# Loads .env and runs create_demo_db.sql inside the running Postgres container.
#
# -----------------------------------------------------------------------------

set -euo pipefail

cd "$(dirname "$0")"

set -a; . ./.env; set +a

: "${DATABASE_CONTAINER_NAME:?not set in .env}"
: "${PG_ADMIN_USER:?not set in .env}"
: "${DEMO_DB:?not set in .env}"
: "${DEMO_ROLE:?not set in .env}"
: "${DEMO_PASSWORD:?not set in .env}"

echo "Waiting for ${DATABASE_CONTAINER_NAME} to accept connections..."
until docker exec "$DATABASE_CONTAINER_NAME" pg_isready -U "$PG_ADMIN_USER" -q; do
  sleep 1
done

docker exec -i "$DATABASE_CONTAINER_NAME" \
  psql -U "$PG_ADMIN_USER" -d postgres \
       -v demo_db="$DEMO_DB" \
       -v demo_role="$DEMO_ROLE" \
       -v demo_password="$DEMO_PASSWORD" \
       -f - < create_demo_db.sql

