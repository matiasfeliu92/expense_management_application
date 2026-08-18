"""Pytest fixtures that exercise the running Docker container over HTTP.

Tests hit the API at `http://localhost:8000` (the `fastapi_app` container) rather
than an in-process app, so `docker compose up --build` must be up first. Because
there is no reset endpoint, per-test isolation truncates the shared SQLite file
(`expense_app.db`, mounted into the container as `/app/data/expense_app.db`) with
a direct `sqlite3` connection; seeded categories are left untouched.
"""

import pathlib
import sqlite3

import httpx
import pytest

BASE_URL = "http://localhost:8000"

# The container's DB is `sqlite:////app/data/expense_app.db`, which the bind mount
# maps onto the repo-root `expense_app.db` file. We point the same raw sqlite3
# connection at that physical file to reset data between tests.
DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "expense_app.db"


@pytest.fixture(scope="session", autouse=True)
def container_ready():
    """Fail fast with an actionable message if the Docker container is not up."""
    try:
        with httpx.Client(base_url=BASE_URL, timeout=5) as check_client:
            response = check_client.get("/")
            assert response.status_code == 200
    except Exception as exc:
        pytest.fail(
            f"API not reachable at {BASE_URL} ({exc}). "
            "Start the container first: `docker compose up --build`"
        )


@pytest.fixture(autouse=True)
def truncate_tables(container_ready):
    """Delete user data from the shared DB before every test.

    Runs the deletes in foreign-key order (operations → accounts → users) and
    deliberately keeps `categories`, which are seeded once by the container's
    entrypoint and shared across tests."""
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute("DELETE FROM operations")
        connection.execute("DELETE FROM accounts")
        connection.execute("DELETE FROM users")
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(scope="session")
def client():
    """Plain HTTP client pointed at the container's public port."""
    with httpx.Client(base_url=BASE_URL) as http_client:
        yield http_client


@pytest.fixture
def category():
    """Return the id of an active, predefined category.

    Categories are seeded by the container's entrypoint and never truncated, so we
    reuse the first active one. Only if the catalog were somehow empty (it should
    not be) do we insert a fallback row directly into the shared DB."""
    connection = sqlite3.connect(DB_PATH)
    try:
        row = connection.execute(
            "SELECT id FROM categories WHERE is_active = 1 ORDER BY id LIMIT 1"
        ).fetchone()
        if row is None:
            cursor = connection.execute(
                "INSERT INTO categories (name, description, is_active) VALUES (?, ?, 1)",
                ("test category", "Inserted by tests when the catalog is empty"),
            )
            connection.commit()
            return cursor.lastrowid
        return row[0]
    finally:
        connection.close()


@pytest.fixture
def auth_headers(client):
    """Factory fixture: registers (if needed) and logs in a user, returning a ready-to-use
    `Authorization` header dict. Call it more than once with different emails to
    get headers for distinct users within the same test."""
    def _register_and_login(name="matute92", email="matumazparrote@gmail.com", password="francia"):
        client.post("/users/new", json={"name": name, "email": email, "password": password})
        response = client.post("/users/login", json={"email": email, "password": password})
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _register_and_login