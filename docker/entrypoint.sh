#!/bin/bash
set -e

echo "Starting Fuel Consumption Record Application..."

# 确保数据目录存在（LinuxServer.io 规范）
mkdir -p /data

# 设置默认数据库路径（如果未通过环境变量指定）
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:////data/fuel.db}"

# 启动 FastAPI 后端（后台运行）
echo "Starting FastAPI backend..."
echo "Database: $DATABASE_URL"
cd /app/server

# 首次运行：自动初始化数据库
if [ ! -f /data/fuel.db ]; then
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
