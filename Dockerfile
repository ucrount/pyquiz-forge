# ---------- Stage 1: build frontend ----------
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Install deps first (cache layer)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-fund --no-audit

# Build
COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: backend + frontend dist ----------
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

# Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Backend source
COPY app ./app
COPY scripts ./scripts

# Frontend dist -> served by FastAPI as static files
COPY --from=frontend-builder /build/dist ./app/static

# Runtime dirs (mounted as volumes in compose)
RUN mkdir -p /app/data /app/logs

EXPOSE 8000

CMD ["sh", "-c", "python -m scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]
