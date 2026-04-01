FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

RUN apk add libpq

RUN mkdir /app

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

CMD ["python3", "job.py"]