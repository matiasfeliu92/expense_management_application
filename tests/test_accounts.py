import pytest


def test_create_account_returns_201(client, auth_headers):
    headers = auth_headers()
    response = client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=headers)

    assert response.status_code == 201
    account = response.json()
    assert account["name"] == "Home"
    assert account["currency"] == "USD"
    assert account["balance"] == 0.0
    assert account["is_active"] is True
    assert account["id"] > 0


def test_create_account_rejects_unsupported_currency(client, auth_headers):
    headers = auth_headers()
    response = client.post("/accounts/new", json={"name": "Home", "currency": "EUR"}, headers=headers)

    assert response.status_code == 422
    assert "unsupported currency" in response.text.lower()


def test_create_account_requires_auth(client):
    response = client.post("/accounts/new", json={"name": "Home", "currency": "USD"})

    assert response.status_code == 401


def test_create_duplicate_account_name_returns_400(client, auth_headers):
    headers = auth_headers()
    first = client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=headers)
    assert first.status_code == 201

    second = client.post("/accounts/new", json={"name": "Home", "currency": "ARS"}, headers=headers)

    assert second.status_code == 400
    assert "already exists" in second.json()["detail"]


def test_accounts_are_isolated_between_users(client, auth_headers):
    user_one = auth_headers()
    user_two = auth_headers(name="another_user", email="another@example.com")

    client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=user_one)

    user_two_accounts = client.get("/accounts/", headers=user_two).json()
    user_one_accounts = client.get("/accounts/", headers=user_one).json()

    assert user_two_accounts == []
    assert len(user_one_accounts) == 1


def test_get_accounts_returns_only_active(client, auth_headers):
    headers = auth_headers()
    client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=headers)

    accounts = client.get("/accounts/", headers=headers).json()

    assert len(accounts) == 1
    assert accounts[0]["name"] == "Home"
    assert accounts[0]["balance"] == 0.0