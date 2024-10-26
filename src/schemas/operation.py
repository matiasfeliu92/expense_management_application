from datetime import datetime
from pydantic import BaseModel

class OperationResponse(BaseModel):
    id: int
    concept: str
    amount: float
    type: str
    date: datetime

    class Config:
        from_attributes = True

    def to_dict(self):
        return self.dict()
    
class CreateOperation(BaseModel):
    concept: str
    amount: float
    type: str
    user_id: int

    def to_dict(self):
        return self.dict()