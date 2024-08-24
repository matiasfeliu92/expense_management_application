from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from auth.auth import create_access_token
from config.db import session
from models.users import User
from schemas.users import UserEntity, UserList, ValidateUser

users_router = APIRouter(prefix="/users")
user = User()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@users_router.get('/', tags=["users"])
def get_users():
    users = session.query(User).all()
    users_list = [UserEntity(**user.to_dict()) for user in users]
    response_data = UserList(users=users_list).model_dump()
    return JSONResponse(content=response_data, status_code=200)

@users_router.get('/id/{id}', tags=["users"])
def get_user_by_id(id: int):
    user = session.query(User).filter(User.id == id).first()
    if user:
        user_entity = UserEntity(**user.__dict__)
        return JSONResponse(content=user_entity.model_dump(), status_code=200)
    else:
        return JSONResponse(
            status_code=404, content={"Detail": f"Cannot find the request user with id: {id}"}
        )
    
@users_router.get('/name/{name}', tags=["users"])
def get_user_by_name(name: str):
    user = session.query(User).filter(User.name.ilike(f"%{name}%")).first()
    if user:
        user_entity = UserEntity(**user.__dict__)
        return JSONResponse(content=user_entity.model_dump(), status_code=200)
    else:
        return JSONResponse(
            status_code=404, content={"Detail": f"Cannot find the request user with name: {name}"}
        )
    
@users_router.post('/new', tags=["users"])
def signup(user: UserEntity):
    try:
        print("------------NEW USER---------------")
        print(user)
        user_found = session.query(User).filter((User.name == user.name) | (User.email == user.email)).first()
        if user_found:
            return JSONResponse(
                status_code=409,
                content={"detail": f"The user {user.name} and email {user.email} is already registered"},
            )
        hashed_password = pwd_context.hash(user.password)
        # hashed_password= user.hash_password(user.password)
        print("------------HASHED PASSWORD---------------")
        print(hashed_password)
        new_user = User(name=user.name, email=user.email, password=hashed_password, balance=user.balance)
        print(new_user)
        session.add(new_user)
        session.commit()
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during user creation.")
    
@users_router.post('/login', tags=["users"])
def login(user: ValidateUser):
    user_found = session.query(User).filter(User.email == user.email).first()
    # if not user_found:
    #     return JSONResponse(
    #         status_code=409,
    #         content={"detail": f"The email {user.email} is not registered"},
    #     )
    # print("----------VALIDACION DE CONTRASEÑAS------------")
    # # print({'validation_result': User.verify_password(user.password, user_found.password)})
    # print({'validation_result': pwd_context.verify(user.password, user_found.password)})
    if not user_found or not pwd_context.verify(user.password, user_found.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}