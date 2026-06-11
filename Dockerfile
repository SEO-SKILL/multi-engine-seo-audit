FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project
COPY pyproject.toml ./
RUN uv pip install --system flask

COPY . .
RUN uv pip install --system -e . || true

EXPOSE 8080
CMD ["python", "web_dashboard.py"]
