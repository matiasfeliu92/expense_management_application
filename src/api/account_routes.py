"""Routes for listing and creating the authenticated user's accounts."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas import AccountResponse, AccountCreate
from ..db.config import get_db
from ..services import AccountService

class AccountRoutes:
    """Registers `GET /accounts/` and `POST /accounts/new`. Both require a valid
    `Authorization` header, set by `LoadUserData`."""

    def __init__(self):
        self.router = APIRouter(prefix="/accounts")
        self.router.add_api_route("/", self.get_accounts, response_model=List[AccountResponse], methods=["GET"])
        self.router.add_api_route("/new", self.create_account, response_model=AccountResponse, methods=["POST"])

    @staticmethod
    def get_accounts(request: Request, db: Session = Depends(get_db)):
        """List the authenticated user's own accounts."""
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        account_service = AccountService(db)
        accounts = account_service.get_by_user(user['id'])
        return accounts

    @staticmethod
    def create_account(account: AccountCreate, request: Request, db: Session = Depends(get_db)):
        """Create a new account owned by the authenticated user."""
        user = request.state.user
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")
        account_service = AccountService(db)
        new_account = account_service.create_new(user['id'], account)
        return new_account