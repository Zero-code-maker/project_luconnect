from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt
from API.database import create_user
from API import database
from API.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, authenticate_user_and_generate_token, create_access_token
from API.models import Token, TokenRefresh, User, UserCreate

router = APIRouter()

@router.post("/auth/register", response_model=User)
async def register_new_user(user: UserCreate, conn = Depends(database.get_connection)):
    try:
        return create_user(conn, user)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), conn = Depends(database.get_connection)):
    token = authenticate_user_and_generate_token(conn, form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/auth/refresh-token", response_model=Token)
async def refresh_token(token_refresh: TokenRefresh):
    decoded_token = jwt.decode(token_refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    username = decoded_token.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="As credências não são válidas.", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
