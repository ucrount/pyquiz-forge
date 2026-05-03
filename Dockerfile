# ---------- Stage 1: build frontend ----------
FROM node:20-alpine AS frontend-builder

# Override these via docker compose `build.args` or `--build-arg` if you need
# faster mirrors (e.g. China network). Default is the official npm registry.
ARG NPM_REGISTRY=https://registry.npmjs.org

WORKDIR /build
RUN npm config set registry "$NPM_REGISTRY"

# Install deps first (cache layer)
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-fund --no-audit

# Build
COPY frontend/ ./
RUN npm run build


# ---------- Stage 2: backend + frontend dist ----------
FROM python:3.11-slim

# Override via build args for China network etc.
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG APT_MIRROR=

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_INDEX_URL=$PIP_INDEX_URL \
    TZ=Asia/Shanghai

WORKDIR /app

# Optional apt mirror swap (e.g. mirrors.tuna.tsinghua.edu.cn for China users)
RUN if [ -n "$APT_MIRROR" ]; then \
        sed -i "s|http://deb.debian.org|https://$APT_MIRROR|g" /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
        sed -i "s|http://deb.debian.org|https://$APT_MIRROR|g" /etc/apt/sources.list 2>/dev/null || true; \
    fi

# System deps for tzdata + healthcheck curl
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps (uses PIP_INDEX_URL env above)
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
