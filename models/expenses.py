from config.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key = True, nullable=False, autoincrement="auto")
    concept = Column(String(50), nullable=True)
    amount = Column(Integer, nullable=True)
    type = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    createdAt = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="expenses")

    def to_dict(self):
        return {
            "concept": self.concept,
            "amount": self.amount,
            "type": self.type,
            "user_id": self.user_id,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }