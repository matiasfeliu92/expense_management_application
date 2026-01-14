import pytest

from src_v2.domain.value_objects import Name, Email, Password, Balance, Id
from src_v2.domain.exceptions import NegativeBalanceError, BalanceZeroError


def test_name_valid():
    n = Name("Alice")
    assert n.value == "Alice"


def test_name_invalid_empty():
    with pytest.raises(ValueError):
        Name("")


def test_email_valid():
    e = Email("user1@hotmail.com")
    assert e.value == "user1@hotmail.com"


def test_email_invalid():
    with pytest.raises(ValueError):
        Email("not-an-email")


def test_password_valid():
    p = Password("strongpass")
    assert p.value == "strongpass"


def test_password_short():
    with pytest.raises(ValueError):
        Password("short")


def test_balance_negative():
    with pytest.raises(NegativeBalanceError):
        Balance(-1)


def test_balance_zero_not_allowed():
    with pytest.raises(BalanceZeroError):
        Balance(0, allow_zero=False)


def test_balance_default_ok():
    b = Balance(0)
    assert b.value == 0


def test_id_optional_and_validation():
    id_none = Id(None)
    assert id_none.value is None
    with pytest.raises(ValueError):
        Id(0)
