"""Pydantic schemas for creating and reading operations (income/expense entries)."""

from datetime import datetime
from pydantic import BaseModel

class OperationResponse(BaseModel):
    """Operation read model."""

    id: int
    concept: str
    amount: float
    type: str
    currency: str
    date: datetime
    account_id: int
    category_id: int

    class Config:
        from_attributes = True

    def to_dict(self):
        return self.dict()

class CreateOperation(BaseModel):
    """Operation creation payload. `account_id` must belong to the authenticated
    user; the service is responsible for enforcing that, not this schema."""

    concept: str
    amount: float
    type: str
    account_id: int
    category_id: int

    def to_dict(self):
        return self.dict()