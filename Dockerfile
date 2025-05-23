FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
RUN pip install --default-timeout=100 -r requirements.txt