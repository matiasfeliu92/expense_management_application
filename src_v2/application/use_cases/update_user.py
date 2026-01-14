from src_v2.domain.entities.user import User
from src_v2.domain.repositories.user_repository import UserRepository
from src_v2.domain.exceptions import UserNotFoundError


class UpdateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, user: User) -> User:
        if user.id is None or user.id.value is None:
            raise ValueError("User id is required for update")
        existing = self.repo.get_by_id(user.id)
        if existing is None:
            raise UserNotFoundError(f"User with id={user.id.value} not found")
        return self.repo.update(user)
