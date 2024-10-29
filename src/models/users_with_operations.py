from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

from . import User, Operation
from ..db.config import SessionLocal

session = SessionLocal()

view = session.query(
    User.id.label('user_id'),
    User.name,
    User.email,
    Operation.concept,
    Operation.amount,
    Operation.type,
    Operation.date
).outerjoin(Operation, User.id == Operation.user_id).all()