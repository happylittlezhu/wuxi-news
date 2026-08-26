#!/bin/bash
# 推送到 GitHub（带网络探测与重试，应对 github.com 间歇性阻断）
# 探测目标用 api.github.com（连接稳定），push 目标 github.com 失败则重试
# 用法: bash push_to_github.sh [提交信息]
cd "$(dirname "$0")"

# 若有提交信息则先提交
if [ -n "$1" ]; then
  git add -A
  git commit -m "$1" || echo "(nothing to commit)"
fi

echo "开始推送（最多20次尝试，每次间隔8秒）..."
for i in $(seq 1 20); do
  # 用稳定的 api.github.com 探测外网连通性
  if curl -s -o /dev/null --connect-timeout 6 https://api.github.com 2>/dev/null; then
    echo "[$i] 网络已通，执行推送..."
    if git push origin main 2>&1; then
      echo "PUSH_OK"
      exit 0
    fi
    echo "[$i] push 失败（github.com 波动），继续重试"
  else
    echo "[$i] 外网不通，等待 8 秒..."
  fi
  sleep 8
done

echo "PUSH_FAILED: 20次尝试均未成功"
exit 1
