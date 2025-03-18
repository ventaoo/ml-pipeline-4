#!/bin/bash

# 读取解密后的文件内容并导出为环境变量
export DB_HOST=$(jq -r '.db_host' /shared/db_info.json)
export DB_PORT=$(jq -r '.db_port' /shared/db_info.json)
export DB_NAME=$(jq -r '.db_name' /shared/db_info.json)
export DB_USER=$(jq -r '.db_user' /shared/db_info.json)
export DB_PASSWORD=$(jq -r '.db_password' /shared/db_info.json)
