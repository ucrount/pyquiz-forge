FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Asia/Shanghai

WORKDIR /app

# System deps for tzdata + healthcheck curl
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata curl \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first (layer cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source
COPY app ./app
COPY scripts ./scripts

# Runtime dirs (will be mounted as volumes in compose)
RUN mkdir -p /app/data /app/logs

EXPOSE 8000

# Init DB + seed learning path, then start service
CMD ["sh", "-c", "python -m scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
