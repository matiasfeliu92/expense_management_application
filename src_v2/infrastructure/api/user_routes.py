from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from src_v2.infrastructure.db.config import get_db
from src_v2.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src_v2.application.services.user_service import UserService
from src_v2.infrastructure.schemas.user import UserResponse, UserCreate, UserUpdate
from src_v2.domain.value_objects import Name, Email, Password, Balance, Id
from src_v2.domain.exceptions import UserNotFoundError, NegativeBalanceError, BalanceZeroError, DomainError
from src_v2.domain.entities.user import User as DomainUser


router = APIRouter(prefix="/v2/users")


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    users = service.list_all()
    return [UserResponse(**u.to_dict()) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        user = service.get_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")
    return UserResponse(**user.to_dict())


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        created = service.create(payload.name, payload.email, payload.password, payload.balance)
    except (ValueError, DomainError) as exc:
        # ValueError can come from VO validation; DomainError from domain rules
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return UserResponse(**created.to_dict())


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    id_vo = Id(user_id)

    try:
        existing = service.get_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    name_vo = payload.name if payload.name is not None else existing.name
    email_vo = payload.email if payload.email is not None else existing.email
    password_vo = payload.password if payload.password is not None else existing.password
    balance_vo = payload.balance if payload.balance is not None else existing.balance

    domain_user = DomainUser(id=id_vo, name=name_vo, email=email_vo, password=password_vo, balance=balance_vo)
    try:
        updated = service.update(domain_user)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except (ValueError, NegativeBalanceError, BalanceZeroError, DomainError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return UserResponse(**updated.to_dict())


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    repo = SQLAlchemyUserRepository(db)
    service = UserService(repo)
    try:
        service.delete(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
