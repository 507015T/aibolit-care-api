FROM python:3.13-slim-bookworm AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_VERSION=0.0.0 \
    PIP_UVICORN_VERSION=0.34.0

WORKDIR /app_dir

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-editable --index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

RUN uv pip install -e . --index-url https://pypi.tuna.tsinghua.edu.cn/simple
FROM base AS final

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY --from=builder /app_dir /app_dir
WORKDIR /app_dir
CMD ["uv", "run", "sh", "-c", "alembic upgrade head && uvicorn src.aibolit.main:make_app --factory --no-server-header --proxy-headers --workers 1 --host 0.0.0.0 --port 8000"]
