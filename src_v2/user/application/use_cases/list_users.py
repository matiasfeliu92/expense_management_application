from typing import List

from src_v2.user.domain.entities.user import User
from src_v2.user.domain.repositories.user_repository import UserRepository


class ListUsers:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self) -> List[User]:
        return self.repo.list_all()
