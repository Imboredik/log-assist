# ---- Билд этап ----
FROM python:3.13 AS builder
LABEL authors="Asriel_Story"

RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Финальный этап ----
FROM python:3.13-slim
WORKDIR /app

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends libpq5 curl &&  \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

ENV SSH_TUNNELING="false" \
    SSH_HOST="url.example.com" \
    SSH_USER="ssh_user" \
    SSH_PASSWORD="password" \
    SSH_PORT="22" \
    PG_HOST="localhost" \
    PG_PORT="5432" \
    PG_USER="user" \
    PG_PASSWORD="password" \
    PG_DATABASE="log-assist" \
    SECRET_KEY="secret_key" \
    ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="1800" \
    OPENROUTER_API_KEY="key..." \
    OPENROUTER_URL="https://openrouter.ai/api/v1/chat/completions" \
    OPENROUTER_MODEL="qwen/qwen2.5-vl-32b-instruct:free" \
    MINIO_ENDPOINT="localhost:9000" \
    MINIO_ACCESS_KEY="admin" \
    MINIO_SECRET_KEY="password" \
    MINIO_SECURE="False" \
    MAX_IMAGE_SIZE="2048" \
    MAX_IMAGE_COUNT="2" \
    MAX_CONTEXT_TOKENS="131072" \
    MAX_OUTPUT_TOKENS="1024"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s CMD curl http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] # Добавлен --reload для обновления во время разработки
