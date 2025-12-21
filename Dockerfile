FROM python:3.12-alpine

LABEL authors="Samartha Madhyastha"

RUN mkdir /app

COPY . /app

RUN pip install -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]