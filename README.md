# Lu Connect

## Descrição
Este é um projeto desenvolvido com FastAPI e PostgreSQL para que forneça dados e funcionalidades para facilitar a
comunicação entre o time comercial, os clientes e a empresa.

## Pré-requisitos
Certifique-se de ter o Python instalado em sua máquina. Além disso, crie um ambiente virtual e instale as dependências do projeto usando:

```bash
pip install -r requirements.txt
```
## Configuração do Banco de Dados

Crie o arquivo .env e configure as variáveis de ambiente para o PostgreSQL.

```bash
DATABASE_URL=postgresql://localhost/mydb?user=other&password=secret 
```
## Executando o Projeto

Para iniciar o servidor, execute o seguinte comando:

```bash
uvicorn API.main:app --reload
```
O servidor estará disponível em http://localhost:8000.

Endpoints

  Autenticação:
  
    POST /auth/login: Autenticação de usuário.
    POST /auth/register: Registro de novo usuário.
    POST /auth/refresh-token: Refresh de token JWT.
    
  Clientes:
  
    GET /clients: Listar todos os clientes, com suporte a paginação e filtro por nome e email.
    POST /clients: Criar um novo cliente, validando email e CPF únicos.
    GET /clients/{id}:Listar um cliente específico.
    PUT /clients/{id}: Atualizar informações de um cliente específico.
    DELETE /clients/{id}: Excluir um cliente.
  
  Produtos:
  
    GET /products: Listar todos os produtos, com suporte a paginação e filtros por categoria, preço e disponibilidade.
    POST /products: Criar um novo produto, contendo os seguintes atributos: descrição, valor de venda, código de
    barras, seção, estoque inicial, e data de validade (quando aplicável) e imagens.
    GET /products/{id}: Obter informações de um produto específico.
    PUT /products/{id}: Atualizar informações de um produto específico.
    DELETE /products/{id}: Excluir um produto.

  Pedidos:
  
    GET /orders: Listar todos os pedidos, incluindo os seguintes filtros: período, seção dos produtos, id_pedido, status do
    pedido e cliente.
    POST /orders: Criar um novo pedido contendo múltiplos produtos, validando estoque disponível.
    GET /orders/{id}: Obter informações de um pedido específico.
    PUT /orders/{id}: Atualizar informações de um pedido específico, incluindo status do pedido
    DELETE /orders/{id}: Excluir um pedido.   
        
Certifique-se de revisar a documentação da API em http://localhost:8000/docs para obter detalhes sobre como usar cada endpoint.

## Licença
GNU GENERAL PUBLIC LICENSE [Licença GPL](./LICENSE.md).
