# Usa imagem oficial Python slim (menor tamanho)
FROM python:3.13-slim

# Define diretório de trabalho
WORKDIR /code

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências primeiro (para aproveitar cache do Docker)
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copia código da aplicação
COPY ./app /code/app
COPY ./frontend /code/frontend

# Cria diretório para o banco de dados
RUN mkdir -p /code/data

# Expõe porta da aplicação
EXPOSE 8000

# Comando para iniciar a aplicação
# Usa uvicorn diretamente para melhor controle
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Para produção, use (sem --reload):
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
