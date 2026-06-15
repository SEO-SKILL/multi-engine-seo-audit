FROM python:3.12-slim AS base

# 系统依赖：lxml 需要 libxml2/libxslt，curl 用于 healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
      libxml2 libxslt1.1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# uv（极速包管理）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# 先装依赖（利用 Docker 层缓存）
COPY pyproject.toml ./
RUN uv pip install --system --no-cache \
      anthropic beautifulsoup4 diskcache flask httpx jinja2 jsonschema \
      lxml orjson pydantic pyyaml structlog tenacity typer

# 业务代码
COPY . .

ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8080/api/health || exit 1

CMD ["python", "web_dashboard.py"]
