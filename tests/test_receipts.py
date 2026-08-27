import pytest

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"0" * 32


@pytest.fixture
def account(client, auth_headers, category):
    """Create an account via the API and return its id plus auth headers."""
    headers = auth_headers()
    response = client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=headers)
    assert response.status_code == 201
    return {"id": response.json()["id"], "headers": headers}


def test_from_receipt_without_token_returns_401(client, account):
    response = client.post(
        "/operations/from-receipt",
        files={"file": ("receipt.png", PNG_BYTES, "image/png")},
        data={"account_id": str(account["id"])},
    )

    assert response.status_code == 401


def test_from_receipt_with_unsupported_extension_returns_422(client, account):
    """Extension validation runs before any DB/AI work, so no API key is needed."""
    response = client.post(
        "/operations/from-receipt",
        files={"file": ("receipt.txt", b"hello", "text/plain")},
        data={"account_id": str(account["id"])},
        headers=account["headers"],
    )

    assert response.status_code == 422
    assert "Unsupported receipt format" in response.json()["detail"]


def test_from_receipt_with_unknown_account_returns_404(client, account):
    response = client.post(
        "/operations/from-receipt",
        files={"file": ("receipt.png", PNG_BYTES, "image/png")},
        data={"account_id": "999999"},
        headers=account["headers"],
    )

    assert response.status_code == 404


def test_from_receipt_on_foreign_account_returns_403(client, account):
    other = client.post(
        "/users/new",
        json={"name": "intruder", "email": "intruder@example.com", "password": "secret"},
    )
    assert other.status_code == 201
    login = client.post("/users/login", json={"email": "intruder@example.com", "password": "secret"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        "/operations/from-receipt",
        files={"file": ("receipt.png", PNG_BYTES, "image/png")},
        data={"account_id": str(account["id"])},
        headers=other_headers,
    )

    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"]