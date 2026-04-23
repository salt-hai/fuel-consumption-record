#!/bin/bash
set -e

echo "Starting Fuel Consumption Record Application..."

# 确保数据目录存在
mkdir -p /app/data

# 启动 FastAPI 后端（后台运行）
echo "Starting FastAPI backend..."
cd /app/server

# 首次运行：自动初始化数据库
if [ ! -f /app/data/fuel.db ]; then
    echo "Initializing database..."
    python -c "from database import init_db; import asyncio; asyncio.run(init_db())"
fi

# 启动 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 等待后端启动
sleep 3

# 启动 Nginx 前台运行
echo "Starting Nginx..."
nginx -g 'daemon off;'
