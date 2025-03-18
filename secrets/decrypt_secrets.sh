#!/bin/bash
echo "=== Start decryption ==="

# 从环境变量获取 Vault 密码并生成临时文件
VAULT_PASSWORD_FILE=$(mktemp)
echo "$VAULT_PASSWORD" > $VAULT_PASSWORD_FILE

# 解密配置文件
ansible-vault decrypt ./db_info.json.enc \
  --vault-password-file $VAULT_PASSWORD_FILE \
  --output ./db_info.json

# 检查解密是否成功
if [ $? -ne 0 ]; then
  echo "Error: Decryption failed!"
  rm -f $VAULT_PASSWORD_FILE
  exit 1
fi

# 导出环境变量（需安装 jq）
export $(jq -r 'to_entries|map("\(.key)=\(.value)")|.[]' ./db_info.json)

# 彻底删除临时文件
shred -u $VAULT_PASSWORD_FILE ./db_info.json

echo "=== End decryption ==="