from src_v2.user.domain.entities.user import User
from src_v2.user.domain.value_objects import Name, Email, Password, Balance, Id


def test_user_to_dict():
    name = Name("Bob")
    email = Email("bob@example.com")
    password = Password("password1")
    balance = Balance(10)
    user = User(name=name, email=email, password=password, id=Id(1), balance=balance)
    d = user.to_dict()
    assert d["id"] == 1
    assert d["name"] == "Bob"
    assert d["email"] == "bob@example.com"
    assert d["balance"] == 10
    assert d["is_active"] is True
