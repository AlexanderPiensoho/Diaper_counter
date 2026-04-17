# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
docker-compose up        # build and start all services (app on localhost:2000)
docker-compose down      # stop all services
docker-compose up --build  # rebuild after dependency changes
```

Local dev (no Docker):
```bash
pip install -r requirements.txt
python -m app.main       # starts uvicorn on localhost:8000
```

Requires a running MariaDB instance and a `.env` file with DB credentials.

## Architecture

3-tier containerized app: FastAPI backend + MariaDB + vanilla JS frontend served as static files.

```
app/
  main.py      # FastAPI entry, mounts /static, serves index.html at root
  routes.py    # API router: /changes/, /sleep/, /food/ (POST + GET each)
  crud.py      # raw MariaDB queries + tz helpers (_as_utc / _to_naive_utc)
  schemas.py   # Pydantic models for diaper/sleep/food Create+Read
  db.py        # connection context manager
  static/
    index.html # entire frontend (Swedish UI, Tailwind CDN, vanilla JS, 3 tabs)

init_db/
  01-schema.sql     # adults, baby, change_types, diaper_changes
  02-data.sql       # seeds 7 adults, 1 baby, 3 change types
  03-sleep-food.sql # sleep_sessions, food_intake

tests/
  unit/          # mocked DB, fast
  integration/   # real MariaDB required
```

**Timezone invariant:** Backend stores naive UTC in MariaDB, wraps as `+00:00`-aware on read. Frontend converts `datetime-local` inputs via `new Date(v).toISOString()` before POSTing. Breaking this means timestamps drift by the user's UTC offset.

Docker Compose maps host port 2000 → container port 8000. The app service depends on MariaDB being healthy before starting.

## Data Model

- `change_types`: 1=pee, 2=poo, 3=routine
- `diaper_changes` links adult → baby → change_type, with `accident` bool and auto-timestamp
- No ORM — all SQL is written directly in `crud.py`

## Environment

`.env` is required and not committed. It must define:
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (plus the `MARIADB_*` equivalents for the DB container).

## Testing

```bash
pip install -r requirements-dev.txt

# Unit tests (mocked DB, ~80% coverage gate enforced)
pytest tests/unit

# Integration tests require a real MariaDB. Start the DB container first:
docker-compose up -d db
DB_HOST=127.0.0.1 DB_PORT=3306 DB_USER=root DB_PASSWORD=$MARIADB_PASSWORD DB_NAME=diaper_counter \
    pytest tests/integration --no-cov
```

The `mariadb` Python driver requires MariaDB Connector/C (`brew install mariadb-connector-c` on macOS).

CI (`.github/workflows/ci.yml`) runs four jobs in parallel after a blocking `secret-scan` gate: unit tests with coverage gate, integration tests against a service-container MariaDB, and a Docker build validation. Deploy is manual.
