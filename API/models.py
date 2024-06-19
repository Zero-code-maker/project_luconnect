from pydantic import BaseModel, EmailStr, ConfigDict
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

    
