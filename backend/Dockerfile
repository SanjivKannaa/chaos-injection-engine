FROM python:3.8-slim
WORKDIR /app
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install flask flask-jwt-extended flask-sqlalchemy flask-migrate pymysql flask-cors argon2-cffi python-dotenv cryptography
