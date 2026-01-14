from typing import Optional

from src_v2.domain.value_objects import Name, Email, Password, Balance
from src_v2.domain.entities.user import User
from src_v2.domain.repositories.user_repository import UserRepository


class CreateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def __call__(self, name: str, email: str, password: str, balance: int = 0) -> User:
        name_vo = Name(name)
        email_vo = Email(email)
        password_vo = Password(password)
        balance_vo = Balance(balance)

        user = User(name=name_vo, email=email_vo, password=password_vo, balance=balance_vo)
        return self.repo.add(user)
