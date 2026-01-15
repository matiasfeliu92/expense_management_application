from typing import List, Optional

from sqlalchemy.orm import Session

from src_v2.user.infrastructure.models.user import User as UserORM

from src_v2.user.domain.entities.user import User as DomainUser
from src_v2.user.domain.value_objects import Name, Email, Password, Balance, Id
from src_v2.user.domain.repositories.user_repository import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def _to_domain(self, orm_user: UserORM) -> DomainUser:
        id_vo = Id(orm_user.id) if orm_user.id is not None else None
        name_vo = Name(orm_user.name)
        email_vo = Email(orm_user.email)
        password_vo = Password(orm_user.password) if orm_user.password is not None else Password("")
        balance_vo = Balance(orm_user.balance if orm_user.balance is not None else 0)
        # operations mapping omitted: return empty list; infra can implement if needed
        return DomainUser(name=name_vo, email=email_vo, password=password_vo, id=id_vo, balance=balance_vo, operations=[])

    def _from_domain(self, user: DomainUser) -> UserORM:
        orm = UserORM()
        if user.id is not None and user.id.value is not None:
            orm.id = user.id.value
        orm.name = user.name.value
        orm.email = user.email.value
        orm.password = user.password.value
        orm.balance = user.balance.value
        return orm

    def add(self, user: DomainUser) -> DomainUser:
        orm_user = self._from_domain(user)
        self.session.add(orm_user)
        self.session.commit()
        self.session.refresh(orm_user)
        return self._to_domain(orm_user)

    def get_by_id(self, id: Id) -> Optional[DomainUser]:
        orm_user = self.session.query(UserORM).filter(UserORM.id == id.value).one_or_none()
        if orm_user is None:
            return None
        return self._to_domain(orm_user)

    def get_by_email(self, email: Email) -> Optional[DomainUser]:
        orm_user = self.session.query(UserORM).filter(UserORM.email == email.value).one_or_none()
        if orm_user is None:
            return None
        return self._to_domain(orm_user)

    def list_all(self) -> List[DomainUser]:
        orm_users = self.session.query(UserORM).all()
        return [self._to_domain(u) for u in orm_users]

    def update(self, user: DomainUser) -> DomainUser:
        if user.id is None or user.id.value is None:
            raise ValueError("User id is required for update")
        orm_user = self.session.query(UserORM).get(user.id.value)
        if orm_user is None:
            raise ValueError("User not found")
        orm_user.name = user.name.value
        orm_user.email = user.email.value
        orm_user.password = user.password.value
        orm_user.balance = user.balance.value
        self.session.add(orm_user)
        self.session.commit()
        self.session.refresh(orm_user)
        return self._to_domain(orm_user)

    def delete(self, id: Id) -> None:
        orm_user = self.session.query(UserORM).get(id.value)
        if orm_user is None:
            return
        self.session.delete(orm_user)
        self.session.commit()
