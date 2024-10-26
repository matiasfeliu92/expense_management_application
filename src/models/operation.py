from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import datetime
from enum import Enum as PyEnum

from src.db.config import Base

class OperationType(str,PyEnum):
    expense = 'Expense'
    income = "Income"

class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True, index=True)
    concept = Column(String(250), index=True)
    amount = Column(Float)
    type = Column(SQLEnum(OperationType), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="operations")

    def to_dict(self):
        return {
            "id": self.id,
            "concept": self.concept,
            "amount": self.amount,
            "type": self.type,
            "date": self.date.isoformat(),  # Ensure proper date formatting
            "user_id": self.user_id
        }