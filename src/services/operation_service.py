"""Business logic for recording operations and keeping account balances in sync."""

from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ..core import Security
from ..models import Operation, OperationType, Account, Category
from ..schemas import CreateOperation

# Accepts both the Spanish and English spellings the client historically sent,
# so existing callers don't break when this was tightened to an exact match.
TYPE_ALIASES = {
    'egreso': OperationType.expense,
    'ingreso': OperationType.income,
    'expense': OperationType.expense,
    'income': OperationType.income,
}

class OperationService():
    """Wraps the `Operation` queries and the balance-affecting create flow
    exposed through `OperationRoutes`."""

    def __init__(self, db: Session):
        self.db = db
        self.security= Security()

    def _normalize_type(self, raw_type: str) -> OperationType:
        """Resolve a client-supplied type string to an `OperationType`, 400 if unrecognized."""
        op_type = TYPE_ALIASES.get(raw_type.lower())
        if op_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not valid operation type, you must enter one of {sorted(TYPE_ALIASES.keys())}",
            )
        return op_type

    def get_by_user(self, user_id: int):
        """List every operation across all of the user's accounts."""
        operations = self.db.query(Operation).join(Account).filter(Account.user_id == user_id).all()
        operations_dict = [operation.to_dict() for operation in operations]
        return JSONResponse(content=operations_dict, status_code=status.HTTP_200_OK)

    def get_by_user_and_id(self, user_id: int, id: int):
        """Fetch a single operation, scoped to accounts owned by the user."""
        operation = self.db.query(Operation).join(Account).filter(
            and_(Account.user_id == user_id, Operation.id == id)
        ).first()
        if not operation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found")
        return JSONResponse(content=operation.to_dict(), status_code=status.HTTP_200_OK)

    def create_new(self, user_id: int, operation: CreateOperation):
        """Create an operation and apply its effect to the target account's balance.

        Locks the account row (`with_for_update`) for the duration of the balance
        update to avoid lost updates under concurrent writes — this only provides
        real row locking on MySQL; SQLite (used in tests/dev) ignores it. Rejects
        the operation with 403 if the account doesn't belong to the caller, and
        with 400 if applying it would take the balance negative.
        """
        category = self.db.query(Category).filter(
            Category.id == operation.category_id, Category.is_active == True
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The category with id {operation.category_id} does not exist or is inactive.",
            )

        op_type = self._normalize_type(operation.type)

        try:
            account = self.db.query(Account).filter(
                Account.id == operation.account_id
            ).with_for_update().first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            if account.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account does not belong to the authenticated user",
                )

            amount = Decimal(str(operation.amount))
            delta = amount if op_type == OperationType.income else -amount
            new_balance = account.balance + delta
            if new_balance < 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

            new_operation = Operation(
                concept=operation.concept,
                amount=amount,
                type=op_type,
                currency=account.currency,
                account_id=account.id,
                category_id=category.id,
            )
            account.balance = new_balance
            self.db.add(new_operation)
            self.db.commit()
            self.db.refresh(new_operation)
        except Exception:
            self.db.rollback()
            raise

        return JSONResponse(content=new_operation.to_dict(), status_code=status.HTTP_201_CREATED)