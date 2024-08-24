from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class Expense_by_User(BaseModel):
    user_name: str
    user_email: str
    expense_concept: str
    expense_amount: int
    expense_type: str
    # created_at: date
    # updated_at: date

    # @property
    # def created_at_date(self):
    #     return self.created_at.date()

    # @property
    # def updated_at_date(self):
    #     return self.updated_at.date()

class Expenses_by_User_List(BaseModel):
    expenses: List[Expense_by_User]