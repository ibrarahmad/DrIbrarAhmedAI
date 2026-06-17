-- health_reader.sql — create the read-only role the agent uses.
-- Companion to "OpenClaw Runs a Real Local Tool" (@DrIbrarAhmedAI).
--
-- The agent NEVER connects as `postgres`. It uses this least-privilege role:
--   • no superuser   • no writes   • no DDL   • pg_monitor (read stats) only
--
-- Run as a superuser against your application database:
--   psql -h localhost -U postgres -d appdb -f health_reader.sql
--
-- ⚠️  Set a strong password. Do not commit the real one — replace the
--     placeholder below, or pass it in:
--       psql -v pw="'$(openssl rand -base64 24)'" -f health_reader.sql

\set pw '''REPLACE_WITH_A_STRONG_PASSWORD'''

create user health_reader with password :pw;

grant connect on database appdb to health_reader;
grant pg_monitor to health_reader;          -- read pg_stat_* views, no data access
grant usage on schema public to health_reader;

-- verify
\du health_reader
