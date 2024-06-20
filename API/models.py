from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional

##### Autenticação #####

class UserBase(BaseModel):
    username: str
    email: EmailStr
    primeiro_nome: Optional[str] = None
    segundo_nome: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    password: str
    #is_admin: bool = False  # Adicionando campo para identificar se é administrador
    
    @classmethod
    def json_schema_extra(cls, schema, model):
        schema['properties']['password'] = schema['properties'].pop('hashed_password')
        return schema

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str
    
##### Cliente #####

class ClientBase(BaseModel):
    nome: str
    email: EmailStr
    cpf: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None

class Client(ClientBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)