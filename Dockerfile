FROM python:3.14-alpine

LABEL authors="Samartha Madhyastha"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add libpq

COPY . /app

WORKDIR /app

RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]