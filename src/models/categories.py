from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum, Text, String
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from src.db.config import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    description = Column(Text)
    operation = relationship("Operation", back_populates="categories")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }