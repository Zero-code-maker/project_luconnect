from fastapi import HTTPException, status
from jwt import PyJWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import ExpiredSignatureError, jwt
from API.models import User, Token
from API.database import get_user
from API.config import get_secret_key

SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(conn, username: str, password: str) -> User:
    user = get_user(conn, username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalido username ou password")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalido username or password")
    return user

def authenticate_user_and_generate_token(conn, username: str, password: str):
    user = authenticate_user(conn, username, password)
    if not user:
        return None
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode["exp"] = expire
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

