from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    balance: int

    def to_dict(self):
        return self.dict()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    balance: float
    is_active: bool

    class Config:
        from_attributes = True

    def to_dict(self):
        return self.dict()

class UserLogin(BaseModel):
    email: str
    password: str

    def to_dict(self):
        return self.dict()