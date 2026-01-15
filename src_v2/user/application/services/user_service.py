from typing import List, Optional

from src_v2.user.domain.entities.user import User as DomainUser
from src_v2.user.domain.repositories.user_repository import UserRepository
from src_v2.user.application.use_cases.create_user import CreateUser
from src_v2.user.application.use_cases.get_user_by_id import GetUserById
from src_v2.user.application.use_cases.get_user_by_email import GetUserByEmail
from src_v2.user.application.use_cases.list_users import ListUsers
from src_v2.user.application.use_cases.update_user import UpdateUser
from src_v2.user.application.use_cases.delete_user import DeleteUser


class UserService:
    """Application service that delegates to use-case classes."""

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def create(self, name: str, email: str, password: str, balance: int = 0) -> DomainUser:
        return CreateUser(self.repo)(name=name, email=email, password=password, balance=balance)

    def get_by_id(self, id: int) -> DomainUser:
        return GetUserById(self.repo).__call__(id)

    def get_by_email(self, email: str) -> DomainUser:
        return GetUserByEmail(self.repo).__call__(email)

    def list_all(self) -> List[DomainUser]:
        return ListUsers(self.repo).__call__()

    def update(self, user: DomainUser) -> DomainUser:
        return UpdateUser(self.repo).__call__(user)

    def delete(self, id: int) -> None:
        return DeleteUser(self.repo).__call__(id)
