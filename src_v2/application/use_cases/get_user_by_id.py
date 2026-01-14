from typing import Optional

from src_v2.domain.value_objects.id import Id
from src_v2.domain.entities.user import User
from src_v2.domain.repositories.user_repository import UserRepository
from src_v2.domain.exceptions import UserNotFoundError


class GetUserById:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, id: int) -> User:
        id_vo = Id(id)
        user = self.repo.get_by_id(id_vo)
        if user is None:
            raise UserNotFoundError(f"User with id={id} not found")
        return user
