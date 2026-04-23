# 汽车油耗记录系统

一个移动优先的汽车油耗记录 Web 应用，支持多车辆管理、加油记录、油耗统计、保养提醒等功能。

## 功能特性

- 🔐 简单密码认证
- 🚗 多车辆管理
- ⛽ 加油记录（日期、里程、金额、油量等）
- 📊 油耗统计与趋势图表
- 🔔 保养提醒
- 📥 数据导出（CSV/Excel）
- 📱 移动端优先设计
- 🐳 Docker 一键部署

## 技术栈

### 前端
- Vue 3 (Composition API + TypeScript)
- Vite
- Vant 4（移动端组件库）
- Tailwind CSS
- ECharts（图表）
- Pinia（状态管理）

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- SQLite
- Alembic（数据库迁移）

### 部署
- Docker + Nginx（单镜像多阶段构建）

## 快速开始

### Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/fuel-consumption-record.git
cd fuel-consumption-record

# 构建镜像
docker build -t fuel-record:latest .

# 运行容器
docker run -d \
  --name fuel-record \
  -p 80:80 \
  -v fuel-data:/app/data \
  --restart unless-stopped \
  fuel-record:latest

# 访问 http://localhost
```

### 开发环境

#### 前端开发
```bash
cd client
pnpm install
pnpm dev
# 访问 http://localhost:5173
```

#### 后端开发
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
# API 地址 http://localhost:8000
```

### Docker Compose 开发
```bash
# 启动前后端（热重载）
docker compose up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

## 项目结构

```
fuel-consumption-record/
├── client/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 可复用组件
│   │   ├── stores/         # Pinia 状态
│   │   ├── api/            # API 请求
│   │   ├── router/         # 路由配置
│   │   └── utils/          # 工具函数
│   └── ...
├── server/                 # FastAPI 后端
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic schemas
│   ├── routers/            # API 路由
│   └── main.py
├── docker/                 # Docker 配置
│   ├── nginx.conf
│   └── entrypoint.sh
├── Dockerfile              # 生产环境多阶段构建
├── docker-compose.yml      # 开发环境
└── README.md
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

## 数据备份

```bash
# 备份 SQLite 数据库
docker cp fuel-record:/app/data/fuel.db ./backup-$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup.db fuel-record:/app/data/fuel.db
```

## 许可证

MIT License
