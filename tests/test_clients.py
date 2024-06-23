from fastapi.testclient import TestClient
from API.main import app
from API.database import get_connection
from API.config import get_secret_key
import jwt

client = TestClient(app)
SECRET_KEY = get_secret_key()

# Função para obter autenticação
def get_auth_header():
    token_data = {"sub": "testuser"}
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

# Testa a rota de obtenção de todos os clientes
def test_get_all_clients():
    with get_connection() as conn:
        response = client.get("/clients", headers=get_auth_header())
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

# Testa a rota de obtenção para o cliente com ID 6        
def test_get_client_by_id():
    with get_connection() as conn:
        response_get = client.get("/clients/6", headers=get_auth_header())
        
        assert response_get.status_code == 200
        data = response_get.json()
        assert data["id"] == 6
        assert data["nome"] == "Cliente Teste"
        assert data["cpf"] == 12345678901
        assert data["email"] == "cliente@teste.com"
        
        
        
                