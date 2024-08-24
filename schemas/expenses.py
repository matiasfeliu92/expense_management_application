import datetime
from typing import List, Optional
from pydantic import BaseModel

class ExpenseBase(BaseModel):
    concept: Optional[str]
    amount: Optional[int]
    type: Optional[str]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        arbitrary_types_allowed = True

class UserWithExpenses(BaseModel):
    name: str
    email: str
    balance: Optional[int]
    expenses: List[ExpenseBase]

    class Config:
        orm_mode = True