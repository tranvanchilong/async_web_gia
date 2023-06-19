FROM python:3.10.6-slim-bullseye

WORKDIR /app

COPY ./app/requirements.txt .

RUN pip install requests

RUN pip install -r requirements.txt
