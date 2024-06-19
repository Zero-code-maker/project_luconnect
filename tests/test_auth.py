from fastapi.testclient import TestClient
from API.main import app
from API.database import get_connection
from API.auth import authenticate_user_and_generate_token
from API.config import get_secret_key
import jwt

client = TestClient(app)

 # Testa a rota de Criar usuario
def test_register_user():
    with get_connection() as conn:
        response = client.post(
            "/auth/register",
            json={"username": "testuser", "email": "test@example.com", "password": "testpassword"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

# Testa a rota de login        
def test_login_for_access_token():
    test_username = "testuser"
    test_password = "testpassword"

    def mock_authenticate_user(username: str, password: str):
        if username == test_username and password == test_password:
            return {"access_token": "mock_access_token", "token_type": "bearer"}
        else:
            return None

    app.dependency_overrides[authenticate_user_and_generate_token] = mock_authenticate_user

    response = client.post(
        "/auth/login",
        data={"username": test_username, "password": test_password}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
# Testa a rota de Token
def test_refresh_token():
    test_username = "testuser"
    test_password = "testpassword"
    secret_key = get_secret_key()

    def mock_authenticate_user(username: str, password: str):
        if username == test_username and password == test_password:
            return {"access_token": "mock_access_token", "token_type": "bearer"}
        else:
            return None

    app.dependency_overrides[authenticate_user_and_generate_token] = mock_authenticate_user

    response = client.post(
        "/auth/login",
        data={"username": test_username, "password": test_password}
    )

    # Verifica se a autenticação foi bem-sucedida e se um token de acesso foi gerado
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    access_token = response.json()["access_token"]

    refresh_token_data = {"sub": test_username}
    refresh_token = jwt.encode(refresh_token_data, secret_key, algorithm="HS256")

    print("Access token before refresh:", access_token)

    response = client.post(
        "/auth/refresh-token",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token}
    )

    # Exibe a resposta após a renovação
    print("Response after refresh:", response.json())

    # Verifica se a renovação foi bem-sucedida e se um novo token de acesso foi gerado
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

    # Verifica se o token de acesso foi atualizado
    assert response.json()["access_token"] == access_token




            

