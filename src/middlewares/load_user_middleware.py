import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from jwt import InvalidTokenError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.security import ALGORITHM, SECRET_KEY
from ..db.config import SessionLocal
from ..models import Operation, User

class LoadUserData(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        request.state.operations = []

        auth_header = request.headers.get("Authorization")
        print("------------------AUTH HEADER--------------")
        print(auth_header)
        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) != 2 or parts[0] != "Bearer":
                return JSONResponse(content={"detail": "Invalid token"}, status_code=401)
            token = parts[1]
            try:
                payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
                print("------------------PAYLOAD--------------")
                print(payload)
                user_id = payload.get("sub")
                print("------------------USER ID--------------")
                print(user_id)
                if user_id:
                    db: Session = SessionLocal()
                    try:
                        user = db.query(User).filter(User.id == int(user_id)).first()
                        if not user:
                            return JSONResponse(content={"detail": "User not found"}, status_code=401)

                        operations = db.query(Operation).filter(Operation.user_id == user.id).all()
                        print("------------------OPERATIONS--------------")
                        print(operations)

                        request.state.user = user.to_dict()
                        request.state.operations = [operation.to_dict() for operation in operations]
                    finally:
                        db.close()
            except InvalidTokenError:
                return JSONResponse(content={"detail": "Invalid token"}, status_code=401)
        print("---------------------------------REQUEST.STATE------------------------------------")
        print(request.state.__dict__)
        response = await call_next(request)
        print("------------------RESPONSE--------------")
        print(response.status_code)
        return response
