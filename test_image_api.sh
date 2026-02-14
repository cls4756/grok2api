#!/bin/bash

echo "=========================================="
echo "测试图片生成API"
echo "=========================================="
echo ""

# 重启服务以应用新的日志
echo "[1] 重启服务..."
docker compose restart grok2api
sleep 5
echo "✓ 服务已重启"
echo ""

# 清空日志
echo "[2] 清空旧日志..."
docker compose logs grok2api --tail 0 > /dev/null 2>&1
echo "✓ 日志已清空"
echo ""

# 测试API调用
echo "[3] 调用图片生成API..."
echo "请求: POST /v1/chat/completions"
echo "模型: grok-imagine-1.0"
echo "提示词: 一只可爱的猫咪"
echo ""

curl -X POST http://192.168.68.193:8004/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer grok2api@ddd" \
  -d '{
    "model": "grok-imagine-1.0",
    "messages": [
      {"role": "user", "content": "一只可爱的猫咪"}
    ]
  }' -v 2>&1 | tee /tmp/api_response.txt

echo ""
echo ""
echo "=========================================="
echo "查看服务日志"
echo "=========================================="
echo ""

# 等待日志写入
sleep 2

# 查看最近的日志
echo "[4] 最近的服务日志:"
docker compose logs grok2api --tail 50 | grep -E "Image generation|Using.*mode|stream=|use_ws=|Chat failed|403|WebSocket"

echo ""
echo ""
echo "=========================================="
echo "分析"
echo "=========================================="
echo ""

# 检查响应
if grep -q "error" /tmp/api_response.txt; then
    echo "❌ API调用失败"
    echo ""
    echo "错误信息:"
    cat /tmp/api_response.txt | grep -A 5 "error"
else
    echo "✓ API调用成功"
    echo ""
    echo "响应预览:"
    cat /tmp/api_response.txt | head -20
fi

echo ""
echo "请将以上完整输出发送给我分析"
