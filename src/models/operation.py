from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import datetime

from src.db.config import Base
from ..enums import OperationType

class Operation(Base):
    __tablename__ = 'operations'
    id = Column(Integer, primary_key=True, index=True)
    concept = Column(String(250), index=True)
    amount = Column(Float)
    type = Column(SQLEnum(OperationType), nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="operations")
    categories = relationship("Category", back_populates="operation")
    category_id = Column(Integer, ForeignKey('categories.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "concept": self.concept,
            "amount": self.amount,
            "type": self.type.value,
            "date": self.date.isoformat(),
            "user_id": self.user_id,
            "category_id": self.category_id,
            "categories": [category.to_dict() for category in self.categories] if hasattr(self.categories, '__iter__') else self.categories.to_dict()
        }