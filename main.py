from fastapi import FastAPI
from config.db import engine, Session, Base
from models import Expense, User
from routes import users_router, expenses_router

app = FastAPI()
print(engine.url)
Base.metadata.create_all(bind=engine)
app.include_router(users_router)
app.include_router(expenses_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}