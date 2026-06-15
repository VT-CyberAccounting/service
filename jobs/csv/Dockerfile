FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add libpq

RUN mkdir /app

COPY . /app

RUN uv sync --locked

WORKDIR /app

CMD ["python3", "job.py"]