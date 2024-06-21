# Use a imagem oficial do Python como base
FROM python:3.10

# Defina o diretório de trabalho
WORKDIR /API

# Copie os arquivos requirements.txt para o contêiner
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o contêiner
COPY . .

# Defina a variável de ambiente para desativar o buffer de saída do Python
ENV PYTHONUNBUFFERED=1

# Execute a aplicação
CMD ["uvicorn", "API.main:app", "--host", "127.0.0.1", "--port", "8000"]
