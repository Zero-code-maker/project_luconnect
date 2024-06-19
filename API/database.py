import psycopg2
from passlib.context import CryptContext
from psycopg2 import sql
from API.models import UserCreate, User
import os
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def user_exists(conn, username: str, email: str) -> bool:
    query = sql.SQL("""
        SELECT EXISTS(SELECT 1 FROM users WHERE username = %s OR email = %s)
    """)
    with conn.cursor() as cur:
        cur.execute(query, (username, email))
        exists = cur.fetchone()[0]
    return exists

def get_connection():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

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
        
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)        

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
