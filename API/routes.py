from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt
from jwt import PyJWTError
from API.database import create_user
from API import database
from API.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, authenticate_user_and_generate_token, create_access_token
from API.models import Client, ClientCreate, ClientUpdate, Token, TokenRefresh, User, UserCreate

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

##### Rotas de autenticação #####

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

##### Rotas de clientes #####

@router.post("/clients", response_model=Client)
async def create_client(client: ClientCreate, conn = Depends(database.get_connection), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        new_client = database.create_client(conn, client)
        if new_client:
            return new_client
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não foi possível criar o cliente",
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
@router.get("/clients", response_model=List[Client])
async def all_client(conn = Depends(database.get_connection), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        clients = database.get_all_clients(conn)
        return clients

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
@router.get("/clients/{client_id}", response_model=Client)
async def get_client_by_id(client_id: int, conn = Depends(database.get_connection), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        client = database.get_client_id(conn, client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado",
            )
        return client

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: int, client_update: ClientUpdate, conn = Depends(database.get_connection), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        updated_client = database.update_client(conn, client_id, client_update)
        if updated_client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado",
            )
        return updated_client

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
@router.delete("/clients/{client_id}", response_model=dict)
async def delete_client(client_id: int, conn = Depends(database.get_connection), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        deleted = database.delete_client(conn, client_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado",
            )
        return {"message": "Cliente excluído com sucesso"}

    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )        