import pytest

from src_v2.application.use_cases.create_user import CreateUser
from src_v2.application.use_cases.get_user_by_id import GetUserById
from src_v2.application.use_cases.get_user_by_email import GetUserByEmail
from src_v2.domain.exceptions import UserNotFoundError
from src_v2.domain.entities.user import User as DomainUser
from src_v2.domain.value_objects import Name, Email, Password, Balance, Id


class FakeRepo:
    def __init__(self):
        self._store = {}
        self._next = 1

    def add(self, user: DomainUser) -> DomainUser:
        user_id = self._next
        self._next += 1
        user.id = Id(user_id)
        self._store[user_id] = user
        return user

    def get_by_id(self, id: Id):
        return self._store.get(id.value)

    def get_by_email(self, email: Email):
        for u in self._store.values():
            if u.email.value == email.value:
                return u
        return None

    def list_all(self):
        return list(self._store.values())

    def update(self, user: DomainUser):
        if user.id is None or user.id.value not in self._store:
            raise ValueError("User not found")
        self._store[user.id.value] = user
        return user

    def delete(self, id: Id):
        self._store.pop(id.value, None)


def test_create_user_use_case_and_getters():
    repo = FakeRepo()
    create = CreateUser(repo)
    user = create("Alice", "alice@example.com", "password1", 5)
    assert user.id.value == 1
    assert user.name.value == "Alice"

    get_id = GetUserById(repo)
    fetched = get_id(5)
    assert fetched.email.value == "alice@example.com"

    get_email = GetUserByEmail(repo)
    fetched2 = get_email("alice@example.com")
    assert fetched2.id.value == 1

    with pytest.raises(UserNotFoundError):
        get_id(999)
