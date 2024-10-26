import json
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ..core import Security
from ..models import User, Operation
from ..schemas import UserCreate, UserLogin, UserResponse

class User_Service():
    def __init__(self, db: Session):
        self.db = db
        self.security= Security()

    def get_all(self) -> UserResponse:
        # users = self.db.query(User).all()
        # users = self.db.query(User).join(Operation).all()
        users = self.db.query(User).options(joinedload(User.operations)).all()
        users_dict = [user.to_dict() for user in users]
        print({'users_list': users_dict})
        for user in users_dict:
            print("-----------------------USER IN USERS_DICT-----------------------------")
            print(user)
            print([operation for operation in user['operations']])
            user.pop('_sa_instance_state', None)
            user['operations'] = [operation for operation in user['operations']]
        print({'users_dict': users_dict})
        return JSONResponse(content=users_dict, status_code=status.HTTP_200_OK)
    
    def get_by_id(self, id: int):
        user = self.db.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user_dict = user.__dict__.copy()
        user_dict.pop('_sa_instance_state', None)
        return JSONResponse(content=user_dict, status_code=status.HTTP_200_OK)
    
    def create_new(self, user: UserCreate):
        if not user.name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not valid username was pass")
        if not user.email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not valid email was pass")
        if not user.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not valid password was pass")
        hashed_password = self.security.hash_password(user.password)
        new_user = User(name=user.name, email=user.email, password=hashed_password, balance=user.balance)
        print({'new_user': new_user})
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        new_user_dict = new_user.__dict__.copy()
        new_user_dict.pop('_sa_instance_state', None)
        return JSONResponse(content=new_user_dict, status_code=status.HTTP_201_CREATED)

    def login(self, user: UserLogin):
        user_ = self.db.query(User).filter(User.email == user.email).first()
        if not user_:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        verify_password = self.security.verify_passwords(user.password, user_.password)
        if not verify_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
        print("-------------USER FOUND----------------------")
        print(user_)
        token = self.security.create_access_token(user.to_dict())
        print(token)
        return token
