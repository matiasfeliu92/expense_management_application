from typing import Optional

from src_v2.user.domain.value_objects.email import Email
from src_v2.user.domain.entities.user import User
from src_v2.user.domain.repositories.user_repository import UserRepository
from src_v2.user.domain.exceptions import UserNotFoundError


class GetUserByEmail:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, email: str) -> User:
        email_vo = Email(email)
        user = self.repo.get_by_email(email_vo)
        if user is None:
            raise UserNotFoundError(f"User with email={email} not found")
        return user
