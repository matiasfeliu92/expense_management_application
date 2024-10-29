from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

class Security:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = "mysecretkey"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def verify_passwords(self, password, hashed_password):
        return self.pwd_context.verify(password, hashed_password)

    def hash_password(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        print("---------------------DATA IN create_access_token FUNCTION------------------------------")
        print(type(data))
        print(data)
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt