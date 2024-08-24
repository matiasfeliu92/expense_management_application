from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import joinedload
from auth.auth import verify_token
from config.db import session
from models.expenses import Expense
from models.users import User
from schemas.expenses import UserWithExpenses
# from schemas.expenses_by_user import Expense_by_User, Expenses_by_User_List

expenses_router = APIRouter(prefix="/expenses")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@expenses_router.get('/', response_model=UserWithExpenses, tags=["expenses"])
def get_expenses(token: str = Depends(oauth2_scheme)):
    print({'token': token})
    user_data = verify_token(token)
    print({'user data': user_data})
    user = (
        session.query(User)
        .filter(User.email == user_data.get("sub"))
        .options(joinedload(User.expenses))  # Realiza el join para cargar las expenses
        .one_or_none()  # Obtiene el único resultado o None
    )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    # user = session.query(User).filter(User.email == user_data.get("sub")).first()
    # if not user:
    #     raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # expenses = session.query(Expense).filter(Expense.user_id == user.id).all()
    # expenses_list = [
    #     Expense_by_User(
    #         user_name=user.name,
    #         user_email=user.email,
    #         expense_concept=expense.concept,
    #         expense_amount=expense.amount,
    #         expense_type=expense.type,
    #         # created_at=expense.createdAt.isoformat(),
    #         # updated_at=expense.updatedAt.isoformat()
    #     ) for expense in expenses
    # ]
    # print("---------------EXPENSES DATA-----------------")
    # print(expenses_list)
    # return JSONResponse(content={'data': expenses_list}, status_code=200)