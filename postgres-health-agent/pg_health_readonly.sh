#!/usr/bin/env bash
#
# pg_health_readonly.sh — read-only PostgreSQL health check
# Companion to "OpenClaw Runs a Real Local Tool" (@DrIbrarAhmedAI).
#
# This is the ONLY thing OpenClaw is allowed to run. It performs read-only
# pg_stat queries as the `health_reader` role and prints labelled output that
# a local model (Ollama) then summarizes. Zero writes, no DDL, no shell freedom.
#
# Install location used in the video:  /opt/openclaw/tools/pg_health_readonly.sh
set -euo pipefail

# --- connection (override via environment if your setup differs) -------------
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-appdb}"
export PGUSER="${PGUSER:-health_reader}"

# Do NOT hardcode the password. Supply it one of two safe ways:
#   1) ~/.pgpass  (preferred):  localhost:5432:appdb:health_reader:<password>
#                               chmod 600 ~/.pgpass
#   2) environment:             export PGPASSWORD='...'  (before running)
# If PGPASSWORD is unset, libpq falls back to ~/.pgpass automatically.
: "${PGPASSWORD:=}"
[ -n "${PGPASSWORD}" ] || unset PGPASSWORD

echo "SERVER_STATUS"
pg_isready

echo "CONNECTIONS"
psql -Atc "select count(*) from pg_stat_activity;"

echo "ACTIVITY_BY_STATE"
psql -c "select state, count(*) from pg_stat_activity group by state;"

echo "CACHE_HIT_RATIO"
psql -c "select datname, round(100.0*blks_hit/nullif(blks_hit+blks_read,0),2) as cache_hit_pct from pg_stat_database;"

echo "DATABASE_SIZE"
psql -Atc "select pg_size_pretty(pg_database_size(current_database()));"

echo "REPLICATION_LAG"
psql -Atc "select coalesce(now()-pg_last_xact_replay_timestamp(), interval '0 seconds');"
