import pytest


@pytest.fixture
def account(client, auth_headers, category):
    """Create an account via the API and return its id, tagged to the current user."""
    headers = auth_headers()
    response = client.post("/accounts/new", json={"name": "Home", "currency": "USD"}, headers=headers)
    assert response.status_code == 201
    account_id = response.json()["id"]
    return {"id": account_id, "headers": headers, "category_id": category}


def test_create_expense_operation(client, account):
    funded = client.post(
        "/operations/new",
        json={
            "concept": "Salary",
            "amount": 500,
            "type": "ingreso",
            "account_id": account["id"],
            "category_id": account["category_id"],
        },
        headers=account["headers"],
    )
    assert funded.status_code == 201

    response = client.post(
        "/operations/new",
        json={
            "concept": "Groceries",
            "amount": 100.5,
            "type": "egreso",
            "account_id": account["id"],
            "category_id": account["category_id"],
        },
        headers=account["headers"],
    )

    assert response.status_code == 201
    operation = response.json()
    assert operation["concept"] == "Groceries"
    assert operation["amount"] == 100.5
    assert operation["type"] == "Expense"
    assert operation["currency"] == "USD"


def test_balance_reflects_operations(client, account):
    headers = account["headers"]

    client.post(
        "/operations/new",
        json={"concept": "Salary", "amount": 1000, "type": "ingreso", "account_id": account["id"], "category_id": account["category_id"]},
        headers=headers,
    )
    client.post(
        "/operations/new",
        json={"concept": "Rent", "amount": 300, "type": "egreso", "account_id": account["id"], "category_id": account["category_id"]},
        headers=headers,
    )

    accounts = client.get("/accounts/", headers=headers).json()
    assert accounts[0]["balance"] == 700.0


def test_expense_over_balance_returns_400(client, account):
    response = client.post(
        "/operations/new",
        json={"concept": "Too much", "amount": 500, "type": "egreso", "account_id": account["id"], "category_id": account["category_id"]},
        headers=account["headers"],
    )

    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]


def test_operation_with_invalid_type_returns_400(client, account):
    response = client.post(
        "/operations/new",
        json={"concept": "Something", "amount": 10, "type": "transfer", "account_id": account["id"], "category_id": account["category_id"]},
        headers=account["headers"],
    )

    assert response.status_code == 400
    assert "Not valid operation type" in response.json()["detail"]


def test_operation_with_inactive_category_returns_400(client, account, category):
    response = client.post(
        "/operations/new",
        json={"concept": "Groceries", "amount": 10, "type": "egreso", "account_id": account["id"], "category_id": 999999},
        headers=account["headers"],
    )

    assert response.status_code == 400
    assert "does not exist or is inactive" in response.json()["detail"]


def test_operation_on_other_users_account_returns_403(client, account):
    other = client.post(
        "/users/new",
        json={"name": "intruder", "email": "intruder@example.com", "password": "secret"},
    )
    assert other.status_code == 201
    login = client.post("/users/login", json={"email": "intruder@example.com", "password": "secret"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        "/operations/new",
        json={"concept": "Hack", "amount": 10, "type": "egreso", "account_id": account["id"], "category_id": account["category_id"]},
        headers=other_headers,
    )

    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"]


def test_get_operations_filters_by_user(client, account):
    other = client.post(
        "/users/new",
        json={"name": "stranger", "email": "stranger@example.com", "password": "secret"},
    )
    login = client.post("/users/login", json={"email": "stranger@example.com", "password": "secret"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.post(
        "/operations/new",
        json={"concept": "Mine", "amount": 50, "type": "ingreso", "account_id": account["id"], "category_id": account["category_id"]},
        headers=account["headers"],
    )

    mine = client.get("/operations/", headers=account["headers"]).json()
    others = client.get("/operations/", headers=other_headers).json()

    assert len(mine) == 1
    assert others == []