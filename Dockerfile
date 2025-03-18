FROM python:3.11.0-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN chmod +x ./secrets/decrypt_secrets.sh

RUN pip install --default-timeout=100 -r requirements.txt

# 更新系统并安装 Ansible
RUN apt update && apt install -y ansible

# 确保 ansible 可用
RUN ansible --version

CMD ["bash", "-c", "./secrets/decrypt_secrets.sh"]