FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED=1

# 定义构建参数（仅用于构建阶段）
ARG DB_HOST
ARG DB_PORT
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD

# 将凭据注入运行时环境变量
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD


WORKDIR /app

COPY . /app

RUN chmod +x ./secrets/decrypt_secrets.sh

RUN pip install --default-timeout=100 -r requirements.txt

# 更新系统并安装 Ansible
RUN apt update && apt install -y ansible

# 确保 ansible 可用
RUN ansible --version

CMD ["source", "-c", "./secrets/decrypt_secrets.sh"]