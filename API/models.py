from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import date


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
    cpf: int

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[int] = None

class Client(ClientBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
##### Produto #####

class ProductBase(BaseModel):
    descricao: str
    valor_venda: float
    codigo_barras: str = Field(..., max_length=13)
    secao: str
    estoque_inicial: int
    data_validade: Optional[date] = None
    imagens: Optional[List[str]] = []

class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    descricao: Optional[str] = None
    valor_venda: Optional[float] = None
    codigo_barras: Optional[str] = None
    secao: Optional[str] = None
    estoque_inicial: Optional[int] = None
    data_validade: Optional[date] = None
    imagens: Optional[List[str]] = None

class Product(ProductBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
    
##### Pedidos ##### 

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int 

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product

    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    client_id: int
    items: List[OrderItemCreate]

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    total: float
    created_at: date
    client: Client
    items: List[OrderItem]

    model_config = ConfigDict(from_attributes=True)      