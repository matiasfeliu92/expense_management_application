from dataclasses import dataclass, field
from typing import List, Optional, Any

from ..value_objects import Name, Email, Password, Balance, Id


@dataclass
class User:
    """Domain entity representing a user using value objects for fields.

    `name`, `email` and `password` are required (non-optional) value objects.
    """

    name: Name
    email: Email
    password: Password
    id: Optional[Id] = None
    balance: Balance = Balance(0)
    operations: List[Any] = field(default_factory=list)
    is_active: bool = True

    def to_dict(self, include_password: bool = False) -> dict:
        """Return a plain dict with primitive values extracted from value objects."""
        return {
            "id": self.id.value if self.id is not None else None,
            "name": self.name.value,
            "email": self.email.value,
            "balance": self.balance.value,
            "operations_count": len(self.operations) if self.operations is not None else 0,
            "is_active": self.is_active,
            **({"password": self.password.value} if include_password and self.password is not None else {}),
        }