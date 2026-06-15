FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add libpq

WORKDIR /app

COPY . .

RUN uv sync --no-dev

CMD ["python3", "job.py"]