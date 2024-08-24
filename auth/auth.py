from fastapi import HTTPException
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta

SECRET_KEY = "tu_secreto_muy_seguro"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        print({'TOKEN': token})
        print(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print({'PAYLOAD': payload})
        if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
            print("Token ha expirado")
            return None
        return payload
    except JWTError:
        print(f"JWTError: {str(JWTError)}")
        raise HTTPException(status_code=401, detail="Token expired or invalid")