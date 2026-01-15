from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src_v2.user.infrastructure.db.config import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255))
    balance = Column(Integer, default=0)
    # operations = relationship("Operation", back_populates="owner")
    operations = []  # Placeholder; implement relationship if Operation model exists
    is_active = Column(Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "balance": self.balance,
            "operations": [op.to_dict() for op in self.operations] if hasattr(self.operations, '__iter__') else [],
            "is_active": self.is_active,
        }
