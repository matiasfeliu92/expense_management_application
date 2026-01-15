from src_v2.user.domain.value_objects import Balance, Email, Name, Password
from src_v2.user.infrastructure.schemas.user import UserCreate


def test_create_and_get_user(client):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "password1",
        "balance": 5
    }
    resp = client.post("/v2/users/", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["id"] == 1
    assert data["name"] == "Alice"

    # Fetch by id
    resp2 = client.get(f"/v2/users/{data['id']}")
    assert resp2.status_code == 200
    got = resp2.json()
    assert got["email"] == "alice@example.com"
