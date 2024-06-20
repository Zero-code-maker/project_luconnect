from typing import Optional
import psycopg2
from passlib.context import CryptContext
from psycopg2 import sql
from API.models import ClientUpdate, UserCreate, User, ClientCreate, Client
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
        SELECT EXISTS(SELECT 1 FROM clients WHERE email = %s OR cpf = %s)
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
                cpf VARCHAR(14) NOT NULL
            )
        """)
        conn.commit()


def create_client(conn, client: ClientCreate):
    create_client_table(conn)

    if client_exists(conn, client.email, client.cpf):
        raise ValueError("Email ou CPF já existem!")

    nome = client.nome[:255]
    email = client.email[:255]
    cpf = client.cpf[:14]
    
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