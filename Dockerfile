FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN apt update && apt install -y jq && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --default-timeout=100 -r requirements.txt