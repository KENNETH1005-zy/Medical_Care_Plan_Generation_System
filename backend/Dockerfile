FROM python:3.9-slim-buster

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
