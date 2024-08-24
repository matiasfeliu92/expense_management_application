from config.db import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, TIMESTAMP
from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, nullable=False, autoincrement="auto")
    name = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    balance = Column(Integer, nullable=True)

    expenses = relationship("Expense", back_populates="user")

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "balance": self.balance
        }
    
    # def verify_password(self, password: str):
    #     return pwd_context.verify(password, self.hashed_password)
    
    # def hash_password(self, password: str):
    #     self.hashed_password = pwd_context.hash(password)