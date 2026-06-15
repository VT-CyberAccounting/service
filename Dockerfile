FROM node:22-alpine AS ui-builder

WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apk add libpq

RUN mkdir /app

COPY . /app
COPY --from=ui-builder /web/dist /dist

RUN uv sync --locked

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]