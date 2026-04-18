FROM node:22-alpine AS ui-builder

WORKDIR /ui
COPY ui/package*.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

RUN apk add libpq

RUN mkdir /app

COPY . /app
COPY --from=ui-builder /ui/dist /dist

RUN pip install -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]