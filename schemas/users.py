from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class UserEntity(BaseModel):
    name: str
    email: str
    password: str
    balance: Optional[int]

class UserList(BaseModel):
    users: List[UserEntity]

class ValidateUser(BaseModel):
    email: str
    password: str   