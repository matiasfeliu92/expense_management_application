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
- Tables are auto-created, but **categories are not seeded** on local runs. Run only the `INSERT INTO categories` block in `queries.sql` (the `CREATE VIEW user_expenses` above it references a nonexistent `expenses` table — the model table is `operations`; the Docker entrypoint seeds categories automatically). Creating an operation with a `category_id` that isn't active in the DB returns 400.

## Auth

- JWT handled by `LoadUserData` middleware (`src/middlewares/load_user_middleware.py`), not FastAPI dependencies. It decodes the `Authorization: Bearer <token>` header and sets `request.state.user` to a **dict** (`user.to_dict()`), so route/service code uses `user['id']`, not `user.id`. It also preloads the user's operations into `request.state.operations` — resolved via a join through `Account`, since `Operation` has no `user_id` column.
- Tokens use PyJWT (`jwt`), payload is minimal: `sub` (user id) + `exp`/`iat`. `SECRET_KEY` (env `SECRET_KEY`, dev default), `ALGORITHM`, and `PasswordHash` live as module constants in `src/core/security.py`; the middleware imports them from there (single source of truth — do not hardcode elsewhere).
- Passwords are hashed with **argon2** via `pwdlib` (`PasswordHash.recommended()`). Rows hashed under the old passlib/bcrypt will not verify — re-register them.

## Style / structure

- Routes are registered imperatively: each route class's `__init__` calls `self.router.add_api_route(...)`; there are no decorators. New endpoints go in `src/api/*_routes.py`, logic in `src/services/*`. Current sets: `UserRoutes` (`/users`), `AccountRoutes` (`/accounts` — `GET /` lists own active accounts, `POST /new` creates a zero-balance account), `CategoryRoutes` (`/categories` — read-only catalog), `OperationRoutes` (`/operations`).
- Services return `JSONResponse` directly; the `response_model` on routes is effectively bypassed. The `to_dict()` on SQLAlchemy models is the de-facto serializer.
- Account currency is validated against a whitelist in `src/core/currencies.py` (`SUPPORTED_CURRENCIES`, env-overridable via `SUPPORTED_CURRENCIES`, default `USD,ARS`) at the `AccountCreate` schema level (422 on rejection), not in the service or model.
- Service class naming is inconsistent: `User_Service` (snake case) vs `OperationService`/`AccountService`/`CategoryService` — match the existing file's convention.
- Print-based debug statements are pervasive throughout; keep them when touching code (they're part of the current workflow).
- Balance model: `User` holds no balance — money lives in `Account.balance`. Account balance is **derived from operations**: `OperationService.create_new` (in `src/services/operation_service.py`) applies a signed delta (`income` → `+amount`, `expense` → `-amount`, both Spanish and English type strings are accepted) to the owning account and rejects anything that would go negative. There is no manual balance endpoint.
- Gotcha: account ownership is enforced in `OperationService.create_new` by comparing `Account.user_id` against the authenticated user; `CreateOperation` carries only `account_id` + `category_id`, never a raw `user_id`.

## Tests

- `pytest` + `httpx` in `requirements.txt`. Run from repo root: `python -m pytest tests -v` (the `python -m` form is required so the repo root lands on `sys.path` for the `src.*` absolute imports).
- Tests exercise the **running Docker container** over HTTP: the `client` fixture is an `httpx.Client` pointed at `http://localhost:8000`, so `docker compose up --build` must be up first (`container_ready` fixture fails fast with that hint otherwise).
- There is no reset endpoint, so per-test isolation comes from a direct `sqlite3` connection to the shared repo-root `expense_app.db` (the same file the container writes via its `/app/data` bind mount): `truncate_tables` runs `DELETE FROM operations/accounts/users` before every test in FK order. `categories` are **not** truncated — they are seeded once by `scripts/entrypoint.py`; the `category` fixture reuses the first active one (and only inserts a fallback if the catalog were empty).
- Because tests truncate the shared file, a test run wipes users/accounts/operations from the dev DB (categories persist). This is expected.
- `test_auth.py` decodes JWTs with the dev-default `SECRET_KEY`/`ALGORITHM` from `src/core/security.py` — importing that module is safe (no DB side effects); the container runs with the same default.
- Running tests locally requires prior authorization (see Change rules).
