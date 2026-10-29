# SubLedger

A simplified SaaS billing backend: **plans → customers → subscriptions → invoices → payments → ledger**.
Built with FastAPI, SQLAlchemy 2.0, Pydantic v2. Layered design: routes → services → repositories → models.

> Full LLD (ERD, service/repository tables, rule ownership, flows) is in **[DESIGN.md](DESIGN.md)**.

## Project structure

```
app/
  main.py            # app factory, exception handlers, router registration
  config.py          # env-driven settings
  db.py              # engine, session, Base, get_db
  dependencies.py    # dependency wiring (constructor injection)
  exceptions.py      # domain errors -> HTTP mapping
  models/            # SQLAlchemy ORM models + enums
  schemas/           # Pydantic request/response DTOs
  repositories/      # data access only
  services/          # business rules and use cases
  routes/            # thin HTTP layer
tests/               # 25 tests (pytest)
```

## Setup (local)

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                   # optional; defaults to SQLite
uvicorn app.main:app --reload
```
Swagger UI: http://localhost:8000/docs  ·  ReDoc: http://localhost:8000/redoc

## Setup (Docker, Postgres)

```bash
docker compose up --build
```
API on http://localhost:8000, backed by Postgres 16.

## Run tests

```bash
pytest -v
```
Tests use an in-memory SQLite DB and are isolated per test.

## API list

| Method | Path | Purpose |
|---|---|---|
| POST | `/plans` | Create plan (price > 0) |
| GET | `/plans?active_only=` | List plans |
| GET | `/plans/{id}` | Get plan |
| PATCH | `/plans/{id}` | Update price/description |
| POST | `/plans/{id}/activate` · `/deactivate` | Toggle availability |
| POST | `/customers` | Create customer (unique email) |
| GET | `/customers` · `/customers/{id}` | List / get |
| POST | `/subscriptions` | Subscribe customer to plan |
| GET | `/subscriptions?customer_id=` · `/subscriptions/{id}` | List / get |
| POST | `/subscriptions/{id}/cancel` | Cancel |
| POST | `/invoices/generate` | Generate invoice for a subscription (optional period) |
| GET | `/invoices?customer_id=&subscription_id=&status=` · `/invoices/{id}` | List / get |
| GET | `/invoices/{id}/payments` | Payment attempts for invoice |
| POST | `/payments` | Record a payment attempt (success/failed) |
| GET | `/ledger?customer_id=&invoice_id=&reference_id=&entry_type=` | Query ledger |
| GET | `/health` | Health check |

### Example walkthrough

```bash
curl -X POST localhost:8000/plans -H 'content-type: application/json' \
  -d '{"name":"Pro","price":"49.00","currency":"USD","billing_interval":"monthly"}'
curl -X POST localhost:8000/customers -H 'content-type: application/json' \
  -d '{"name":"Asha","email":"asha@example.com"}'
curl -X POST localhost:8000/subscriptions -H 'content-type: application/json' \
  -d '{"customer_id":1,"plan_id":1}'
curl -X POST localhost:8000/invoices/generate -H 'content-type: application/json' \
  -d '{"subscription_id":1}'
curl -X POST localhost:8000/payments -H 'content-type: application/json' \
  -d '{"invoice_id":1,"amount":"20.00","currency":"USD","status":"success","provider_reference":"pay_001"}'
curl "localhost:8000/ledger?invoice_id=1"
```

## Error format & status codes

`{"detail": "message"}` — `404` not found, `409` conflict (duplicate email / active subscription /
invoice period / provider_reference), `422` validation or business-rule violation.

## Assumptions

- The brief's API table was not legible, so the API set above was derived from the functional requirements and core flows.
- Money is `Decimal` / `NUMERIC(12,2)`, serialised in JSON as strings (e.g. `"49.00"`) to avoid float errors.
- Invoice `period_end` is exclusive; default period = today → +1 month (or +12 for yearly plans).
- Invoices are created directly in `issued` status (the `draft` status exists but is unused in the base version).
- A payment's currency must match the invoice currency; no FX.
- `provider_reference` is unique and acts as an idempotency key (retrying the same reference returns 409).
- Changing a plan's price affects future invoices only; existing invoices keep their snapshot.
- Existing subscriptions can still be invoiced if their plan is later deactivated (the rule only blocks *new* subscriptions).

## Limitations

- No authentication/authorisation, pagination, or rate limiting.
- No automatic recurring invoice scheduler (invoices are generated via API).
- No refunds, credit notes, taxes, proration, or multi-currency.
- No migrations (tables are created on startup via `create_all`; use Alembic for production).
- Row locking (`SELECT … FOR UPDATE`) on payment recording is effective on Postgres, a no-op on SQLite.
- Ledger immutability is enforced in the ORM and by the repository API; a DB-level trigger/permission would be needed to block raw SQL edits.
