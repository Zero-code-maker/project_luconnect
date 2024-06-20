# Testes para API

## Descrição
Este arquivo contém testes automatizados para verificar o funcionamento das funcionalidades da API.

## Pré-requisitos
Certifique-se de ter todas as dependências instaladas antes de executar os testes. Recomenda-se utilizar um ambiente virtual para isolar o ambiente de desenvolvimento.

Instale as dependências necessárias com:

```bash
pip install -r requirements.txt
```
## Executando os Testes

Para executar os testes, utilize o seguinte comando:

```bash
pytest test_auth.py
```
## Detalhes dos Testes

Testes Implementados

- test_register_user: Testa a rota de registro de usuário (/auth/register). Verifica se um novo usuário pode ser criado corretamente.

- test_login_for_access_token: Testa a rota de login (/auth/login). Utiliza uma função de mock para simular a autenticação e verifica se um token de acesso é gerado corretamente após o login.

- test_refresh_token: Testa a rota de renovação de token (/auth/refresh-token). Após realizar um login simulado, obtém um token de acesso e utiliza-o para gerar um novo token através da rota de renovação. Verifica se o novo token é gerado corretamente.

## Observações

- Os testes utilizam mocks para simular o processo de autenticação e garantir a independência dos testes do estado do banco de dados ou de recursos externos.
- Certifique-se de que a aplicação esteja rodando localmente ou em um ambiente de testes antes de executar os testes.
