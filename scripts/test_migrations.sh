#!/usr/bin/env bash
#
# Exercise the whole migration chain against a throwaway Postgres container:
#
#   1. upgrade one revision at a time from base to head, snapshotting the
#      schema and row counts after each step
#   2. check that UPDATE stamps modified_at, and that the SQLAlchemy models
#      in app/models match the schema and can load every row
#   3. downgrade one revision at a time, comparing each step with the snapshot
#      taken on the way up
#   4. upgrade base to head in one go, compare with the head snapshot and
#      repeat the modified_at check
#
# The database started by `make up` is not touched.
#
# Environment overrides:
#   TEST_PG_IMAGE  Postgres image (default postgres:$PG_VERSION)
#   ALEMBIC        alembic command (default: uv run --quiet alembic)
#   PYTHON         python command (default: uv run --quiet python)
#
# -----------------------------------------------------------------------------

set -euo pipefail

cd "$(dirname "$0")/.."

env_file=.env
[[ -f $env_file ]] || env_file=setup/env.example
set -a
# shellcheck source=setup/env.example
. "./$env_file"
set +a

image=${TEST_PG_IMAGE:-postgres:${PG_VERSION}}
container=alembic-demo-test-$$
read -r -a alembic <<< "${ALEMBIC:-uv run --quiet alembic}"
read -r -a python <<< "${PYTHON:-uv run --quiet python}"

work=$(mktemp -d)
cleanup() {
    docker rm -f "$container" > /dev/null 2>&1 || true
    rm -rf "$work"
}
trap cleanup EXIT

fail() {
    echo "FAIL: $*" >&2
    exit 1
}


# -----------------------------------------------------------------------------

run_alembic() {
    local out
    if ! out=$("${alembic[@]}" "$@" 2>&1); then
        echo "$out" >&2
        fail "alembic $* from $(current)"
    fi
}

current() {
    local rev
    rev=$("${alembic[@]}" current 2> /dev/null | awk '{print $1}')
    echo "${rev:-base}"
}

psql_api() {
    docker exec -i "$container" \
        psql -X -q -v ON_ERROR_STOP=1 -U "$DEMO_ROLE" -d "$DEMO_DB" "$@"
}

snapshot() {
    # pg_dump emits \restrict lines carrying a random key on every run
    docker exec "$container" \
        pg_dump -U "$DEMO_ROLE" -d "$DEMO_DB" --schema-only --exclude-table=alembic_version \
        | grep -v -E '^\\(un)?restrict '
    psql_api -At <<'SQL'
SELECT format('-- rows in %s: %s', c.relname,
              (xpath('/row/n/text()',
                     query_to_xml(format('SELECT count(*) AS n FROM public.%I', c.relname),
                                  false, true, '')))[1])
  FROM pg_class c
  JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname <> 'alembic_version'
 ORDER BY c.relname;
SQL
}

check_modified_at() {
    psql_api < db/test/check_modified_at.sql 2>&1 | sed 's/^/    /' \
        || fail "modified_at check at $(current)"
}

check_models() {
    "${python[@]}" scripts/check_models.py 2>&1 | sed 's/^/    /' \
        || fail "models do not match the schema at $(current)"
}


# -----------------------------------------------------------------------------

echo "Starting $image as $container"

docker run -d --rm --name "$container" \
    -e POSTGRES_USER="$PG_ADMIN_USER" \
    -e POSTGRES_PASSWORD="$PG_ADMIN_PASSWORD" \
    -p 127.0.0.1::5432 \
    "$image" > /dev/null

# The image's init phase runs a socket-only server first, so a TCP probe
# only succeeds once the real server is up.
for _ in $(seq 60); do
    if docker exec "$container" pg_isready -q -h 127.0.0.1 -U "$PG_ADMIN_USER"; then
        break
    fi
    sleep 1
done
docker exec "$container" pg_isready -q -h 127.0.0.1 -U "$PG_ADMIN_USER" \
    || fail "postgres did not become ready"

export PG_HOST=127.0.0.1
PG_PORT=$(docker port "$container" 5432/tcp | head -1)
export PG_PORT=${PG_PORT##*:}

docker exec -i \
    -e DEMO_ROLE="$DEMO_ROLE" -e DEMO_PASSWORD="$DEMO_PASSWORD" -e DEMO_DB="$DEMO_DB" \
    "$container" psql -X -q -v ON_ERROR_STOP=1 -U "$PG_ADMIN_USER" -d postgres \
    < db/sql/create_api_user.sql

head_rev=$("${alembic[@]}" heads 2> /dev/null | awk '{print $1}')
[[ $(wc -w <<< "$head_rev") -eq 1 ]] || fail "expected one head, got: $head_rev"


# -----------------------------------------------------------------------------

echo "Upgrading one revision at a time"

revs=(base)
snapshot > "$work/base"
while [[ $(current) != "$head_rev" ]]; do
    run_alembic upgrade +1
    rev=$(current)
    revs+=("$rev")
    snapshot > "$work/$rev"
    echo "  ok  up to   $rev"
done

echo "Checking modified_at at head"
check_modified_at

echo "Checking models against the schema at head"
check_models

echo "Downgrading one revision at a time"

for (( i = ${#revs[@]} - 2; i >= 0; i-- )); do
    expected=${revs[i]}
    run_alembic downgrade -1
    [[ $(current) == "$expected" ]] || fail "downgrade landed on $(current), expected $expected"
    snapshot | diff -u "$work/$expected" - \
        || fail "downgrade from ${revs[i + 1]} did not restore the state of $expected"
    echo "  ok  down to $expected"
done

echo "Upgrading base to head in one step"

run_alembic upgrade head
snapshot | diff -u "$work/$head_rev" - \
    || fail "upgrade head from base differs from the stepwise upgrade"
echo "  ok  up to   $head_rev"
check_modified_at

echo "PASS: ${#revs[@]} states, every upgrade and downgrade verified"
