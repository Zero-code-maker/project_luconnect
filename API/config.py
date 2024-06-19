import os
import secrets

def generate_secret_key():
    secret_key = secrets.token_hex(32)
    os.environ['SECRET_KEY'] = secret_key

def get_secret_key():
    return os.environ.get('SECRET_KEY')

if not os.environ.get('SECRET_KEY'):
    generate_secret_key()
