# Database QA Automation

A backend/database-focused test automation project. It ships a small demo REST API (a FastAPI + SQLAlchemy "Users" resource backed by SQLite) alongside a test suite that verifies correctness **at the database level**, not just by trusting the API's response body.

## Why this is different from typical API testing

Most API test suites only check the HTTP response. This project goes one step further: after every write (create/update/delete) through the API, the tests independently query the database directly with raw SQL — bypassing the app's own ORM layer — to confirm the data actually landed correctly. If the app returned `200 OK` but silently failed to persist the change, these tests would catch it.

## Tech Stack

- **FastAPI** + **SQLAlchemy** + **SQLite** — the demo application under test
- **PyTest** + **requests** — the test suite drives the app over real HTTP, like a black-box client
- **sqlite3** (raw SQL) — direct database verification, kept in a separate module from ORM code
- **pytest-html** — self-contained HTML test report

## Project Structure

```
database-qa-automation/
├── app/                          The application under test
│   ├── main.py                   FastAPI endpoints (CRUD for /users)
│   ├── models.py                 SQLAlchemy ORM model
│   ├── schemas.py                Pydantic request/response validation
│   └── database.py               Engine & session setup
├── db_queries/
│   └── user_queries.py           Raw SQL queries — kept separate from test logic
├── tests/
│   ├── conftest.py                starts the API server + DB cleanup fixtures
│   ├── test_data_integrity.py    API write → verified directly in the DB
│   ├── test_crud_verification.py  full CRUD, DELETE confirmed against the DB
│   └── test_negative_cases.py    duplicate keys & invalid data are rejected
├── requirements.txt
└── pytest.ini
```

## Scenarios Covered

- **Data Integrity:** creating/updating a user via the API is verified with a direct SQL query against the database
- **CRUD Verification:** full create → read → update → delete lifecycle; after DELETE, the row is confirmed gone both via the API (404) and via a direct DB query
- **Negative Testing:**
  - duplicate username via the API → `409 Conflict`
  - duplicate primary key inserted directly at the database level → `sqlite3.IntegrityError`
  - invalid email format, username too short, missing required field → `422 Unprocessable Entity`
- **Data cleanup:** an autouse fixture truncates the `users` table before every test, so tests never leak state into each other

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
pytest
```

This starts the FastAPI app on a free local port automatically (no separate terminal needed) and generates a self-contained `report.html` with the results.

You can also run the API on its own to explore it interactively:

```bash
uvicorn app.main:app --reload
# then open http://127.0.0.1:8000/docs
```
