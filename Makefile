#
# Note:
#
# 1) Copy setup/env.example to .env and customize appropriately before using any
#    of these recipes.
#
# -----------------------------------------------------------------------------

PG_VERSION               := $(shell grep -s PG_VERSION               .env | sed 's/.*=//')
PG_PORT                  := $(shell grep -s PG_PORT=                 .env | sed 's/.*=//')
PG_ADMIN_USER            := $(shell grep -s PG_ADMIN_USER            .env | sed 's/.*=//')
PG_ADMIN_PASSWORD        := $(shell grep -s PG_ADMIN_PASSWORD        .env | sed 's/.*=//')
ADMINER_PORT             := $(shell grep -s ADMINER_PORT=            .env | sed 's/.*=//')
DEMO_DB                  := $(shell grep -s DEMO_DB                  .env | sed 's/.*=//')
DEMO_ROLE                := $(shell grep -s DEMO_ROLE                .env | sed 's/.*=//')
DATABASE_CONTAINER_NAME  := $(shell grep -s DATABASE_CONTAINER_NAME= .env | sed 's/.*=//')
ADMINER_CONTAINER_NAME   := $(shell grep -s ADMINER_CONTAINER_NAME=  .env | sed 's/.*=//')


# -----------------------------------------------------------------------------

chk-env:
	@echo "              PG_VERSION |${PG_VERSION}|"
	@echo "                 PG_PORT |${PG_PORT}|"
	@echo "           PG_ADMIN_USER |${PG_ADMIN_USER}|"
	@echo "       PG_ADMIN_PASSWORD |${PG_ADMIN_PASSWORD}|"
	@echo "            ADMINER_PORT |${ADMINER_PORT}|"
	@echo "                 DEMO_DB |${DEMO_DB}|"
	@echo " DATABASE_CONTAINER_NAME |${DATABASE_CONTAINER_NAME}|"
	@echo "  ADMINER_CONTAINER_NAME |${ADMINER_CONTAINER_NAME}|"


clean:
	-rm -rf .venv


# -----------------------------------------------------------------------------

venv:
	uv venv .venv


# -----------------------------------------------------------------------------

# Apply all migrations

upgrade:
	alembic upgrade head

# Verify Current Version

verify:
	alembic current

# To roll back one version

downgrade:
	alembic downgrade -1

# Run every upgrade and downgrade against a throwaway postgres container

test-migrations:
	scripts/test_migrations.sh


# -----------------------------------------------------------------------------
# Add these lines to your ~/.pgpass file to facilitate connection
#
#  127.0.0.1:5433:*:postgres:Secret
#  127.0.0.1:5433:*:api:Much-More-Secret
#
# To tweak the DEMO_USER password use: - update role api set password 'xxxxx';

setup-api-role:
	@echo "Setup api role and demo database..."
	set -a; . ./.env && \
	psql -h 127.0.0.1  -p ${PG_PORT} -U ${PG_ADMIN_USER} -f db/sql/create_api_user.sql

drop-api-role:
	set -a; . ./.env && \
	psql -h 127.0.0.1  -p ${PG_PORT} -U ${PG_ADMIN_USER} -f db/sql/drop_api_user.sql

connect-su:
	psql -h 127.0.0.1 -p ${PG_PORT} -U postgres

connect-api:
	psql -h 127.0.0.1 -p ${PG_PORT} -U ${DEMO_ROLE} -d ${DEMO_DB}


# -----------------------------------------------------------------------------

up:
	docker compose up -d
	docker ps

down:
	docker compose --profile adminer down
	docker ps

destroy:
	docker compose --profile adminer down -v
	docker ps


# -----------------------------------------------------------------------------

.ONESHELL:

reset:
	@echo "Reset the docker environment"
	docker compose --profile adminer down -v --remove-orphans
	sleep 1
	docker compose up -d
	@printf 'Waiting for postgres...'
	@until docker compose exec -T postgres pg_isready -U postgres -h 127.0.0.1 -q; do \
	    printf '.'; sleep 0.5; \
	done
	@echo ' now setup api role...'
	$(MAKE) setup-api-role
	@echo ' ready...'


