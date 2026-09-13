# Bússola Tributária — imagem única (API + site) que roda em qualquer lugar.
# Local (cliente):  docker compose up -d   ->   http://localhost:8000
# Hospedado:        a mesma imagem sobe em Render/Railway/Fly/VPS (usa $PORT se houver).
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Dependências primeiro (melhor cache)
COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Código da API + front-end (site) servido pela própria API
COPY backend/app ./app
COPY frontend ./frontend

EXPOSE 8000

# Honra a variável PORT (hosts como Render/Railway definem uma); cai em 8000 local.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
