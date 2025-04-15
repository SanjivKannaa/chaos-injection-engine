FROM python:3.8-slim

WORKDIR /app

# Install system dependencies and AWS CLI, Terraform
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    groff \
    less \
    ca-certificates \
    zip \
    ansible \
    # Install Terraform
    && wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip \
    && unzip terraform_1.7.5_linux_amd64.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform_1.7.5_linux_amd64.zip \
    # Install AWS CLI v2
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install flask flask-sqlalchemy flask-migrate pymysql flask-cors python-dotenv cryptography chaostoolkit chaostoolkit-aws
