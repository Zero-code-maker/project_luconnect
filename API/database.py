from datetime import datetime
from typing import List, Optional
import psycopg2
from passlib.context import CryptContext
from psycopg2 import sql
from API.models import ClientUpdate, Order, OrderCreate, OrderItem, Product, ProductCreate, UserCreate, User, ClientCreate, Client
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)   

##### Autenticação #####

def user_exists(conn, username: str, email: str) -> bool:
    query = sql.SQL("""
        SELECT EXISTS(SELECT 1 FROM users WHERE username = %s OR email = %s)
    """)
    with conn.cursor() as cur:
        cur.execute(query, (username, email))
        exists = cur.fetchone()[0]
    return exists

def create_user_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                primeiro_nome VARCHAR(255),
                segundo_nome VARCHAR(255),
                hashed_password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
        
def create_user(conn, user: UserCreate):
    create_user_table(conn)
    
    if user_exists(conn, user.username, user.email):
        raise ValueError("Username ou email já existe!")
    
    hashed_password = get_password_hash(user.password)
    primeiro_nome = user.primeiro_nome[:255] if user.primeiro_nome else None
    segundo_nome = user.segundo_nome[:255] if user.segundo_nome else None
    username = user.username[:255]
    email = user.email[:255]
    query = sql.SQL("""
        INSERT INTO users (username, email, primeiro_nome, segundo_nome, hashed_password)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, username, email, primeiro_nome, segundo_nome, hashed_password
    """)
    with conn.cursor() as cur:
        cur.execute(query, (username, email, primeiro_nome, segundo_nome, hashed_password))
        row = cur.fetchone()
        conn.commit()
        if row:
            user_data = {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'primeiro_nome': row[3],
                'segundo_nome': row[4],
                'password': row[5]
            }
            return User(**user_data)
        else:
            return None

def get_user(conn, username: str):
    query = sql.SQL("SELECT id, username, email, primeiro_nome, segundo_nome, hashed_password FROM users WHERE username = %s")
    with conn.cursor() as cur:
        cur.execute(query, (username,))
        row = cur.fetchone()
        if row:
            user_data = {
                'id': row[0],
                'username': row[1],
                'email': row[2],
                'primeiro_nome': row[3],
                'segundo_nome': row[4],
                'password': row[5] if isinstance(row[5], str) else None
            }
            user_data['password'] = user_data.pop('password')
            return User(**user_data)
        else:
            return None

##### Cliente #####

def client_exists(conn, email: str, cpf: str) -> bool:
    query = sql.SQL("""
        SELECT EXISTS(SELECT 1 FROM clients 
        WHERE email = %s OR cpf = %s)
    """)
    with conn.cursor() as cur:
        cur.execute(query, (email, cpf))
        exists = cur.fetchone()[0]
    return exists


def create_client_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                cpf NUMERIC(11, 0) NOT NULL
            )
        """)
        conn.commit()


def create_client(conn, client: ClientCreate):
    create_client_table(conn)

    if client_exists(conn, client.email, client.cpf):
        raise ValueError("Email ou CPF já existem!")

    nome = client.nome[:255]
    email = client.email[:255]
    cpf = str(client.cpf)[:11]
    
    query = sql.SQL("""
        INSERT INTO clients (nome, email, cpf)
        VALUES (%s, %s, %s)
        RETURNING id, nome, email, cpf
    """)
    with conn.cursor() as cur:
        cur.execute(query, (nome, email, cpf))
        row = cur.fetchone()
        conn.commit()
        if row:
            client_data = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'cpf': row[3]
            }
            return Client(**client_data)
        else:
            return None


def get_client_id(conn, client_id: int):
    query = sql.SQL("SELECT id, nome, email, cpf FROM clients WHERE id = %s")
    with conn.cursor() as cur:
        cur.execute(query, (client_id,))
        row = cur.fetchone()
        if row:
            client_data = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'cpf': row[3]
            }
            return Client(**client_data)
        return None


def get_all_clients(conn):
    query = sql.SQL("SELECT id, nome, email, cpf FROM clients")
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        clients = []
        for row in rows:
            client_data = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'cpf': row[3]
            }
            clients.append(Client(**client_data))
        return clients
    
def update_client(conn, client_id: int, client_update: ClientUpdate) -> Optional[Client]:
    query = sql.SQL("""
        UPDATE clients
        SET nome = COALESCE(%s, nome),
            email = COALESCE(%s, email),
            cpf = COALESCE(%s, cpf)
        WHERE id = %s
        RETURNING id, nome, email, cpf
    """)
    with conn.cursor() as cur:
        cur.execute(query, (
            client_update.nome,
            client_update.email,
            client_update.cpf,
            client_id
        ))
        row = cur.fetchone()
        conn.commit()
        if row:
            client_data = {
                'id': row[0],
                'nome': row[1],
                'email': row[2],
                'cpf': row[3]
            }
            return Client(**client_data)
        return None   
    
def delete_client(conn, client_id: int) -> bool:
    query = sql.SQL("DELETE FROM clients WHERE id = %s RETURNING id")
    with conn.cursor() as cur:
        cur.execute(query, (client_id,))
        row = cur.fetchone()
        conn.commit()
        return row is not None
    
##### Produto #####

def create_product_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                descricao TEXT NOT NULL,
                valor_venda NUMERIC(10, 2) NOT NULL,
                codigo_barras VARCHAR(255),
                secao VARCHAR(255),
                estoque_inicial INTEGER,
                data_validade DATE,
                imagens TEXT[]
            )
        """)
        conn.commit()

def create_product(conn, product: ProductCreate) -> Optional[Product]:
    create_product_table(conn)

    query = sql.SQL("""
        INSERT INTO products (descricao, valor_venda, codigo_barras, secao, estoque_inicial, data_validade, imagens)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, descricao, valor_venda, codigo_barras, secao, estoque_inicial, data_validade, imagens
    """)
    with conn.cursor() as cur:
        cur.execute(query, (
            product.descricao,
            product.valor_venda,
            product.codigo_barras,
            product.secao,
            product.estoque_inicial,
            product.data_validade,
            product.imagens
        ))
        row = cur.fetchone()
        conn.commit()
        if row:
            product_data = {
                'id': row[0],
                'descricao': row[1],
                'valor_venda': row[2],
                'codigo_barras': row[3],
                'secao': row[4],
                'estoque_inicial': row[5],
                'data_validade': row[6],
                'imagens': row[7]
            }
            return Product(**product_data)
        return None

def get_product_id(conn, product_id: int) -> Optional[Product]:
    query = sql.SQL("SELECT id, descricao, valor_venda, codigo_barras, secao, estoque_inicial, data_validade, imagens FROM products WHERE id = %s")
    with conn.cursor() as cur:
        cur.execute(query, (product_id,))
        row = cur.fetchone()
        if row:
            product_data = {
                'id': row[0],
                'descricao': row[1],
                'valor_venda': row[2],
                'codigo_barras': row[3],
                'secao': row[4],
                'estoque_inicial': row[5],
                'data_validade': row[6],
                'imagens': row[7]
            }
            return Product(**product_data)
        return None

def get_all_products(conn) -> List[Product]:
    query = sql.SQL("SELECT id, descricao, valor_venda, codigo_barras, secao, estoque_inicial, data_validade, imagens FROM products")
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        products = []
        for row in rows:
            product_data = {
                'id': row[0],
                'descricao': row[1],
                'valor_venda': row[2],
                'codigo_barras': row[3],
                'secao': row[4],
                'estoque_inicial': row[5],
                'data_validade': row[6],
                'imagens': row[7]
            }
            products.append(Product(**product_data))
        return products

def update_product(conn, product_id: int, product_data: ProductCreate) -> Optional[Product]:
    query = sql.SQL("""
        UPDATE products
        SET descricao = COALESCE(%s, descricao),
            valor_venda = COALESCE(%s, valor_venda),
            codigo_barras = COALESCE(%s, codigo_barras),
            secao = COALESCE(%s, secao),
            estoque_inicial = COALESCE(%s, estoque_inicial),
            data_validade = COALESCE(%s, data_validade),
            imagens = COALESCE(%s, imagens)
        WHERE id = %s
        RETURNING id, descricao, valor_venda, codigo_barras, secao, estoque_inicial, data_validade, imagens
    """)
    with conn.cursor() as cur:
        cur.execute(query, (
            product_data.descricao,
            product_data.valor_venda,
            product_data.codigo_barras,
            product_data.secao,
            product_data.estoque_inicial,
            product_data.data_validade,
            product_data.imagens,
            product_id
        ))
        row = cur.fetchone()
        conn.commit()
        if row:
            updated_product_data = {
                'id': row[0],
                'descricao': row[1],
                'valor_venda': row[2],
                'codigo_barras': row[3],
                'secao': row[4],
                'estoque_inicial': row[5],
                'data_validade': row[6],
                'imagens': row[7]
            }
            return Product(**updated_product_data)
        return None

def delete_product(conn, product_id: int) -> bool:
    query = sql.SQL("DELETE FROM products WHERE id = %s RETURNING id")
    with conn.cursor() as cur:
        cur.execute(query, (product_id,))
        row = cur.fetchone()
        conn.commit()
        return row is not None
    
##### Pedidos #####

def create_orders_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(id),
                total NUMERIC(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL
            )
        """)
        conn.commit()

def update_product_stock(conn, product_id: int, quantity: int):
    query = sql.SQL("""
        UPDATE products
        SET estoque_inicial = estoque_inicial - %s
        WHERE id = %s AND estoque_inicial - %s >= 0
        RETURNING id, estoque_inicial
    """)
    with conn.cursor() as cur:
        cur.execute(query, (quantity, product_id, quantity))
        row = cur.fetchone()
        conn.commit()
        if not row:
            raise ValueError(f"Estoque insuficiente para o produto com ID {product_id}")
        updated_stock = row[1]
        if updated_stock < 0:
            raise ValueError(f"Estoque insuficiente para o produto com ID {product_id}")


def create_order(conn, order: OrderCreate) -> Optional[Order]:
    create_orders_table(conn)

    total = 0
    order_items = []
    for item in order.items:
        product = get_product_id(conn, item.product_id)
        if not product:
            raise ValueError(f"Produto com ID {item.product_id} não encontrado")
        if product.estoque_inicial < item.quantity:
            raise ValueError(f"Estoque insuficiente para o produto com ID {item.product_id}")
        total += product.valor_venda * item.quantity

    query = sql.SQL("""
        INSERT INTO orders (client_id, total, created_at)
        VALUES (%s, %s, %s)
        RETURNING id, client_id, total, created_at
    """)
    created_at = datetime.now().date()
    with conn.cursor() as cur:
        cur.execute(query, (order.client_id, total, created_at))
        order_row = cur.fetchone()
        if not order_row:
            return None
        order_id = order_row[0]

        for item in order.items:
            query = sql.SQL("""
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (%s, %s, %s)
                RETURNING id
            """)
            cur.execute(query, (order_id, item.product_id, item.quantity))
            order_item_id = cur.fetchone()[0]
            update_product_stock(conn, item.product_id, item.quantity)

            product = get_product_id(conn, item.product_id)  # Obter o produto atualizado
            order_item = OrderItem(
                id=order_item_id,
                order_id=order_id,
                product=product,
                **item.model_dump()  # Isso copia todos os campos de item para OrderItem
            )
            order_items.append(order_item)

        conn.commit()

        client = get_client_id(conn, order.client_id)  # Obter o cliente
        return Order(
            id=order_row[0],
            client_id=order_row[1],
            total=order_row[2],
            created_at=order_row[3],
            items=order_items,
            client=client
        )
        
def get_all_orders(conn) -> List[Order]:
    query = sql.SQL("""
        SELECT o.id, o.client_id, o.total, o.created_at, c.nome, c.email, c.cpf
        FROM orders o
        JOIN clients c ON o.client_id = c.id
    """)
    with conn.cursor() as cur:
        cur.execute(query)
        order_rows = cur.fetchall()
        orders = []
        for order_row in order_rows:
            client_data = {
                'id': order_row[1],
                'nome': order_row[4],
                'email': order_row[5],
                'cpf': order_row[6]
            }

            query_items = sql.SQL("""
                SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, p.descricao, p.valor_venda, p.codigo_barras, p.secao, p.estoque_inicial, p.data_validade, p.imagens
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """)
            cur.execute(query_items, (order_row[0],))
            items_rows = cur.fetchall()

            items = []
            for row in items_rows:
                product_data = {
                    'id': row[2],
                    'descricao': row[4],
                    'valor_venda': row[5],
                    'codigo_barras': row[6],
                    'secao': row[7],
                    'estoque_inicial': row[8],
                    'data_validade': row[9],
                    'imagens': row[10]
                }
                item_data = {
                    'id': row[0],
                    'order_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'product': Product(**product_data)
                }
                items.append(OrderItem(**item_data))

            order = Order(
                id=order_row[0],
                client_id=order_row[1],
                total=order_row[2],
                created_at=order_row[3],
                client=Client(**client_data),
                items=items
            )
            orders.append(order)

        return orders
