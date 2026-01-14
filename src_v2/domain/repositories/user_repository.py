from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user import User
from ..value_objects.id import Id
from ..value_objects.email import Email


class UserRepository(ABC):
    """Abstract repository interface for `User` domain entity.

    Implementations live in the infrastructure layer and must translate
    between persistence models and the domain `User` entity.
    """

    @abstractmethod
    def add(self, user: User) -> User:
        """Persist a new user and return the created domain entity."""

    @abstractmethod
    def get_by_id(self, id: Id) -> Optional[User]:
        """Return a user by id or `None` if not found."""

    @abstractmethod
    def get_by_email(self, email: Email) -> Optional[User]:
        """Return a user by email or `None` if not found."""

    @abstractmethod
    def list_all(self) -> List[User]:
        """Return all users (careful with large datasets)."""

    @abstractmethod
    def update(self, user: User) -> User:
        """Update an existing user and return the updated domain entity."""

    @abstractmethod
    def delete(self, id: Id) -> None:
        """Delete a user by id."""
