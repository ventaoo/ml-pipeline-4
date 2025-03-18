# secrets/decrypt_secrets.sh
#!/bin/bash
echo "=== Start decryption ==="

# 检查解密密码文件存在
if [ ! -f "./secrets/secret" ]; then
  echo "Error: Vault password file missing!"
  exit 1
fi

# 解密配置文件
ansible-vault decrypt ./secrets/db_info.json.enc \
  --vault-password-file ./secrets/secret \
  --output ./secrets/db_info.json

# 导出环境变量
export $(cat ./secrets/db_info.json | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]')

# 删除临时文件（可选）
shred -u ./secrets/db_info.json

echo "=== End decryption ==="