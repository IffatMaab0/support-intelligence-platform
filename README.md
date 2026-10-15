# ResolveX

ResolveX is a local customer-support application for a fictional company.
Phase 1 implements the complete support workflow without AI: customers submit
tickets, managers assign them, agents respond, and staff keep private notes.

## Technology stack

- Frontend: Streamlit
- Backend API: FastAPI
- Database: PostgreSQL
- Containers: Docker Compose

## Roles

- **Customer** submits tickets, reads their own ticket history, and sends
  follow-up messages.
- **Support Agent** works on assigned tickets, replies to customers, and adds
  internal notes.
- **Manager/Admin** oversees all tickets, assigns agents, changes ticket
  status and priority, manages knowledge documents and agents, and checks
  system status.

## Main workflow

```text
Customer submits ticket
        ↓
Manager assigns an agent
        ↓
Agent replies and adds private notes
        ↓
Customer sees public replies and sends follow-ups
        ↓
Agent or manager resolves the ticket
```

Public messages and internal notes are separate. Customers can never read
private staff notes.

## Prerequisites

Install Docker Desktop and make sure it is running. This project has been
tested with Docker Compose v2.

## First-time setup

1. Clone the repository or open a fresh copy of the project.

2. Create a local environment file from the example:

   ```powershell
   Copy-Item .env.example .env
   ```

3. Open `.env` and replace every `CHANGE_ME` value with one password of your
   choice. Keep `POSTGRES_PASSWORD` and the password inside `DATABASE_URL`
   the same.

   Do not commit `.env`.

4. Build and start the normal application services:

   ```powershell
   docker compose up -d --build
   ```

5. Apply database migrations:

   ```powershell
   docker compose exec api alembic upgrade head
   ```

6. Create the five demo users:

   ```powershell
   docker compose exec -it api python -m app.scripts.seed_users
   ```

   The command asks you to choose a password for each new demo user. Use local
   demo passwords that you can remember; do not write them into the repository.
   If a demo user already exists, the command skips it without changing that
   user.

7. Open the application:

   - Dashboard: <http://localhost:8501>
   - API health check: <http://localhost:8000/health/live>
   - API documentation: <http://localhost:8000/docs>
   - Database browser (Adminer): <http://localhost:8080>

## Demo accounts

The seed script creates these accounts. Their passwords are the local values
entered during the seed step.

| Role | Name | Email |
| --- | --- | --- |
| Customer | Customer A | `customer.a@example.com` |
| Customer | Customer B | `customer.b@example.com` |
| Support Agent | Agent A | `agent.a@example.com` |
| Support Agent | Agent B | `agent.b@example.com` |
| Manager/Admin | Manager/Admin | `manager@example.com` |

## Useful commands

Check service status:

```powershell
docker compose ps
```

Read API logs:

```powershell
docker compose logs -f api
```

Stop the application safely:

```powershell
docker compose down
```

`docker compose down` keeps the PostgreSQL volume, so normal application data
survives the next `docker compose up -d`. Do **not** use `docker compose down
-v` unless you deliberately want to delete all local database data.

## Run the safe automated tests

The test suite uses the separate disposable database
`support_platform_test`. It refuses to run unless `APP_ENV=test` and the test
database name are both correct.

```powershell
docker compose --profile test up -d test-db

docker compose --profile test run --rm --no-deps `
  -e APP_ENV=test `
  -e DATABASE_URL=postgresql+psycopg://test_user:test_password@test-db:5432/support_platform_test `
  api sh -lc "alembic upgrade head && pytest -q"
```

## Local backup and recovery

Task 23 demonstrated a local PostgreSQL backup and restoration into a separate
recovery database. The backup is stored locally under `backups/` and is ignored
by Git. The evidence is recorded in `docs/progress.md`.

A backup file is only a copy. Recovery is proven only after restoring it into a
different database and checking that the records and relationships are usable.

## Architecture in simple words

```text
Browser / Streamlit dashboard
        ↓
FastAPI backend
        ↓
PostgreSQL database
```

- **Streamlit** displays screens and sends requests when a user takes an
  action.
- **FastAPI** authenticates users, checks their role and permissions, applies
  ticket rules, and records the result.
- **PostgreSQL** stores users, tickets, messages, notes, events, knowledge
  documents, and sessions.
- **Docker Compose** starts the local services together and keeps PostgreSQL
  data in a named Docker volume.

## Phase 1 boundary

AI features are intentionally not implemented in Phase 1. The AI Assistant
and AI Review screens are placeholders for Phase 2. This project does not yet
include a chatbot, RAG, embeddings, vector database, sentiment analysis, topic
classification, escalation prediction, model training, cloud deployment, or
CI/CD.
