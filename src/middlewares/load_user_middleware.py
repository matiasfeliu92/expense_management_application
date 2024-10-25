from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..models import User, Operation
from ..db.config import SessionLocal

class LoadUserData(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # self.db_session = Session
        self.SECRET_KEY = "mysecretkey"
        self.ALGORITHM = "HS256"
    
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        print("------------------AUTH HEADER--------------")
        print(auth_header)
        if auth_header:
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                print("------------------PAYLOAD--------------")
                print(payload)
                user_email = payload.get("email")
                print("------------------USER EMAIL--------------")
                print(user_email)
                if user_email:
                    db: Session = SessionLocal()
                    user = db.query(User).filter(User.email == user_email).first()
                    if not user:
                        raise HTTPException(status_code=404, detail="User not found")

                    operations = db.query(Operation).filter(Operation.user_id == user.id).all()
                    print("------------------OPERATIONS--------------")
                    print(operations)

                    request.state.user = user
                    request.state.operations = operations
            except JWTError:
                raise HTTPException(status_code=401, detail="Invalid token")
        response = await call_next(request)
        print("------------------RESPONSE--------------")
        print(response.status_code)
        return response