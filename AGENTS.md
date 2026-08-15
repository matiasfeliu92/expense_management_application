# AGENTS.md

FastAPI + SQLAlchemy (MySQL) expense-tracking API. Python 3.11, deps in `requirements.txt`. No linter, no CI.

## Change rules

- Limit every change to the scope of the requirement at hand. Do not refactor or "improve" unrelated code.
- Do not alter the architecture of the repository/application/system (structure, entrypoints, wiring, dependencies, config, Docker setup).
- Do not alter the database and/or data persistence models (`src/models/*`).
- Do not run tests/checks with Docker or locally without prior authorization.
- Always use object-oriented programming (OOP) in any code written or changed.
- When implementing new functionality or refactoring existing code, add docstring-style comments (docstrings); do not add comments that add no value or meaning.
- Whenever changes are applied, update `AGENTS.md` accordingly.

## Run

- Setup: `python -m venv myenv` + `myenv\Scripts\activate` (Windows) + `pip install -r requirements.txt`. The `myenv` venv is gitignored.
- App (local): `uvicorn src.main:app --reload` — **must run from repo root**. Imports are mixed absolute (`src.models`, `src.db.config`) and relative (`..core.security`), so a `src`-relative cwd or `cd src` will break imports.
- Docker: `docker compose up --build` runs a single `fastapi` container. SQLite DB (`DB_URL=sqlite:////app/data/expense_app.db`) persists via a **bind mount** of the repo's `data/` dir (`./:/app/data`), not a named volume. Dev mode (`./:/app` + `APP_RELOAD=true` → `--reload`) comes from `docker-compose.override.yaml`, applied automatically; run prod-only with `docker compose -f docker-compose.yaml up --build`. `scripts/entrypoint.py` seeds default categories, then launches uvicorn.

## DB config

`src/db/config.py` prefers `DB_URL` when set (e.g. `sqlite:///./expense_app.db` or a full MySQL URL). If unset, builds `mysql+pymysql://` from `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`. SQLite engines get `connect_args={"check_same_thread": False}` automatically. `load_dotenv()` loads `.env`; `.env.example` shows both forms — `DB_URL` wins.

## SQLite notes

- No migrations — `Base.metadata.create_all(bind=engine)` runs at import time in `src/main.py:9`. Edit models, restart to apply. (Alembic is in requirements but unused.)
- The SQLite file (`expense_app.db`, or `data/expense_app.db` in Docker) is gitignored; delete it to reset the schema.
- Tables are auto-created, but **categories are not seeded** on local runs. Run only the `INSERT INTO categories` block in `queries.sql` (the `CREATE VIEW user_expenses` above it references a nonexistent `expenses` table — the model table is `operations`; the Docker entrypoint seeds categories automatically). Creating an operation with a category name that isn't in the DB (matched via case-insensitive substring `ilike('%name%')`) returns 400.

## Auth

- JWT handled by `LoadUserData` middleware (`src/middlewares/load_user_middleware.py`), not FastAPI dependencies. It decodes the `Authorization: Bearer <token>` header and sets `request.state.user` to a **dict** (`user.to_dict()`), so route/service code uses `user['id']`, not `user.id`. It also preloads the user's operations into `request.state.operations`.
- Tokens use PyJWT (`jwt`), payload is minimal: `sub` (user id) + `exp`/`iat`. `SECRET_KEY` (env `SECRET_KEY`, dev default), `ALGORITHM`, and `PasswordHash` live as module constants in `src/core/security.py`; the middleware imports them from there (single source of truth — do not hardcode elsewhere).
- Passwords are hashed with **argon2** via `pwdlib` (`PasswordHash.recommended()`). Rows hashed under the old passlib/bcrypt will not verify — re-register them.

## Style / structure

- Routes are registered imperatively: each route class's `__init__` calls `self.router.add_api_route(...)`; there are no decorators. New endpoints go in `src/api/*_routes.py`, logic in `src/services/*`.
- Services return `JSONResponse` directly; the `response_model` on routes is effectively bypassed. The `to_dict()` on SQLAlchemy models is the de-facto serializer.
- Service class naming is inconsistent: `User_Service` (snake case) vs `OperationService` — match the existing file's convention.
- Print-based debug statements are pervasive throughout; keep them when touching code (they're part of the current workflow).
- Gotcha: `OperationService.create_new` writes the `user_id` from the **request body** (`CreateOperation.user_id`) to the operation row; the authenticated `user_id` argument is only used for the balance lookup. An operation can thus be attributed to a different user than the caller.

## Tests

- `pytest` + `httpx` in `requirements.txt`. Run from repo root: `python -m pytest tests -v` (the `python -m` form is required so the repo root lands on `sys.path` for the `src.*` absolute imports).
- `tests/conftest.py` sets `DB_URL` to a throwaway SQLite file (`tests/test_expense.db`) **before** importing `src.*`, so engine, `SessionLocal` (incl. the middleware's) and `Base.metadata.create_all` in `src/main.py` all target the test DB. Covered by `*.db` in `.gitignore`.
- Isolation: the session fixture creates the file at session start and deletes it at teardown (after `engine.dispose()`); the autouse `truncate_tables` fixture runs `drop_all` + `create_all` before every test, so tests never share rows.
- Running tests locally requires prior authorization (see Change rules).
