# test_protected_route.py

import pytest
import requests

@pytest.fixture
def get_token():
    # Aqui você implementa a lógica para obter um token JWT válido para os testes
    # Exemplo: fazer uma requisição POST para /auth/login e retornar o token recebido
    username = "user2"
    password = "pswtest123"
    login_data = {"username": username, "password": password}
    response = requests.post("http://localhost:8000/auth/login", data=login_data)
    token = response.json()["access_token"]
    return token

def test_protected_route_with_valid_token(get_token):
    # Testa a rota protegida com um token JWT válido
    url = "http://localhost:8000/protected_route"
    headers = {"Authorization": f"Bearer {get_token}"}
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 200
    assert "Rota protegida acessada com sucesso" in response.json()["message"]

def test_protected_route_without_token():
    url = "http://localhost:8000/protected_route"
    response = requests.post(url)
    
    assert response.status_code == 401
    assert "detail" in response.json() and response.json()["detail"] == "Not authenticated"
    
def test_protected_route_with_invalid_token():
    url = "http://localhost:8000/protected_route"
    headers = {"Authorization": "Bearer token_invalido"}
    response = requests.post(url, headers=headers)
    
    assert response.status_code == 401
    assert "detail" in response.json() and response.json()["detail"] == "Could not validate credentials"
