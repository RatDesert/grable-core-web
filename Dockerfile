FROM python:3.10.0-slim-buster

RUN apt-get update -y &&  apt-get upgrade -y && apt-get install -y git gettext

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt