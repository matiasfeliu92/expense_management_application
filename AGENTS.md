# AGENTS.md

FastAPI + SQLAlchemy (MySQL) expense-tracking API. Python 3.11, deps in `requirements.txt`. No tests, no linter, no CI.

## Run

- Setup: `python -m venv myenv` + `myenv\Scripts\activate` (Windows) + `pip install -r requirements.txt`. The `myenv` venv is gitignored.
- App (local): `uvicorn src.main:app --reload` — **must run from repo root**; all imports are absolute (`src.models`, `src.db.config`), so a `src`-relative cwd or `cd src` will break imports.
- Docker: `docker compose up --build` runs a single `fastapi` container with SQLite (`DB_URL=sqlite:////app/data/expense_app.db`, named volume `app_data`). The Python entrypoint (`scripts/entrypoint.py`) seeds default categories on first start and launches uvicorn. Dev mode (bind mount `./:/app` + `--reload`, via `APP_RELOAD=true`) comes from `docker-compose.override.yaml`, active automatically; run prod-only with `docker compose -f docker-compose.yaml up --build`.

## DB config

`src/db/config.py` prefers `DB_URL` when set (enables `sqlite:///./expense_app.db` or a full MySQL URL). If unset, it builds a `mysql+pymysql://` URL from `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`. SQLite engines get `connect_args={"check_same_thread": False}` automatically. `.env.example` shows both forms; `DB_URL` wins.

## SQLite notes

- No migrations — `Base.metadata.create_all(bind=engine)` runs at import time in `src/main.py:9`. Edit models, restart to apply. (Alembic is in requirements but unused.)
- The SQLite file (`expense_app.db`) is gitignored; delete it to reset the schema.
- Tables are auto-created, but **categories are not seeded** on local runs. Run the `INSERT INTO categories` block in `queries.sql` first (the Docker entrypoint `scripts/entrypoint.py` seeds them automatically). Creating an operation with a category name that isn't in the DB (matched via case-insensitive `ilike`) returns 400.

## Auth

- JWT handled by `LoadUserData` middleware (`src/middlewares/load_user_middleware.py`), not FastAPI dependencies. It decodes the `Authorization: Bearer <token>` header and sets `request.state.user` to a **dict** (`user.to_dict()`), so route/service code uses `user['id']`, not `user.id`.
- Tokens use PyJWT (`jwt`), payload is minimal: `sub` (user id) + `exp`/`iat`. `SECRET_KEY` (env `SECRET_KEY`, dev default), `ALGORITHM`, and `PasswordHash` live as module constants in `src/core/security.py`; the middleware imports them from there (single source of truth — do not hardcode elsewhere).
- Passwords are hashed with **argon2** via `pwdlib` (`PasswordHash.recommended()`). Rows hashed under the old passlib/bcrypt will not verify — re-register them.

## Style / structure

- Routes are registered imperatively: each route class's `__init__` calls `self.router.add_api_route(...)`; there are no decorators. New endpoints go in `src/api/*_routes.py`, logic in `src/services/*`.
- Services return `JSONResponse` directly; the `response_model` on routes is effectively bypassed. The `to_dict()` on SQLAlchemy models is the de-facto serializer.
- Service class naming is inconsistent: `User_Service` (snake case) vs `OperationService` — match the existing file's convention.
- Print-based debug statements are pervasive throughout; keep them when touching code (they're part of the current workflow).
