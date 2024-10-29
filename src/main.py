from fastapi import FastAPI
from .db.config import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from .models import User, Operation, Category
from .api import UserRoutes, OperationRoutes
from .middlewares import LoadUserData

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(LoadUserData)

user_routes = UserRoutes().router
operations_router = OperationRoutes().router
app.include_router(user_routes)
app.include_router(operations_router)

@app.get("/")
def read_root():
    print("----------------------------")
    return {"Hello": "World"}