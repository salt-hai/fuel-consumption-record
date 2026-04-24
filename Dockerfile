# ==================== 阶段 1: 构建前端 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/client

# 安装 pnpm
RUN npm install -g pnpm

# 复制前端依赖文件
COPY client/package.json client/pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install --frozen-lockfile

# 复制前端源码并构建
COPY client/ ./
RUN pnpm build

# ==================== 阶段 2: 准备后端 ====================
FROM python:3.11-slim AS backend-builder

WORKDIR /app/server

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY server/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== 阶段 3: 最终镜像 ====================
FROM python:3.11-slim

WORKDIR /app

# 安装 Nginx 和系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制后端依赖和代码
COPY --from=backend-builder /root/.local /root/.local
COPY server/ ./server/

# 确保后端依赖在 PATH 中
ENV PATH=/root/.local/bin:$PATH

# 从前端构建阶段复制静态文件到 Nginx
COPY --from=frontend-builder /app/client/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 创建数据目录（LinuxServer.io 规范）
RUN mkdir -p /data /var/log/nginx && \
    chown -R www-data:www-data /data /usr/share/nginx/html /var/log/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# 启动脚本
ENTRYPOINT ["/entrypoint.sh"]
