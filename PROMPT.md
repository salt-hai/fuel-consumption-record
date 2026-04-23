# 汽车油耗记录系统 — AI Agent 开发提示词

> 将以下内容完整复制给 AI Agent 使用。

---

## 项目背景

开发一个汽车油耗记录 Web 应用，用于个人或家庭记录车辆加油数据、计算油耗、管理多车辆、查看统计图表、设置保养提醒。

## 技术栈

| 层       | 技术                                        |
| -------- | ------------------------------------------- |
| 前端框架 | Vue 3 (Composition API, `<script setup>`) + TypeScript |
| 构建工具 | Vite                                        |
| UI 框架  | Vant 4（移动端组件库）+ Tailwind CSS（辅助样式） |
| 状态管理 | Pinia                                       |
| HTTP 客户端 | Axios                                    |
| 图表     | ECharts 5                                   |
| 后端框架 | Python 3.11+ FastAPI                        |
| ORM      | SQLAlchemy 2.0 (async) + Alembic            |
| 数据库   | SQLite                                      |
| 数据导出 | openpyxl (Excel) / csv                      |
| 容器化   | Docker + Nginx（单文件部署）                |

## 项目结构

```
fuel-consumption-record/
├── client/                    # Vue 3 前端
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── views/             # 页面组件
│   │   │   ├── LoginView.vue       # 登录/密码验证
│   │   │   ├── HomeView.vue        # 首页仪表盘
│   │   │   ├── RecordListView.vue  # 加油记录列表
│   │   │   ├── RecordFormView.vue  # 新增/编辑加油记录
│   │   │   ├── VehicleView.vue     # 车辆管理
│   │   │   ├── StatsView.vue       # 统计分析
│   │   │   ├── MaintenanceView.vue # 保养提醒
│   │   │   └── SettingsView.vue    # 设置
│   │   ├── components/        # 可复用组件
│   │   │   ├── RecordCard.vue      # 记录卡片
│   │   │   ├── StatsChart.vue      # 统计图表
│   │   │   ├── VehicleSelector.vue # 车辆选择器
│   │   │   └── NavBar.vue          # 底部导航栏
│   │   ├── composables/       # 组合式函数
│   │   │   ├── useAuth.ts
│   │   │   ├── useRecords.ts
│   │   │   └── useVehicles.ts
│   │   ├── stores/            # Pinia 状态
│   │   │   ├── auth.ts
│   │   │   ├── records.ts
│   │   │   └── vehicles.ts
│   │   ├── api/               # API 请求
│   │   │   ├── index.ts            # Axios 实例 + 拦截器
│   │   │   ├── auth.ts
│   │   │   ├── records.ts
│   │   │   ├── vehicles.ts
│   │   │   └── stats.ts
│   │   ├── router/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   ├── format.ts           # 金额、日期格式化
│   │   │   └── storage.ts          # localStorage 封装
│   │   └── styles/
│   │       └── main.css
│   └── public/
├── server/                    # FastAPI 后端
│   ├── main.py                # 入口，挂载路由，CORS 配置
│   ├── config.py              # 配置（数据库路径、密钥等）
│   ├── database.py            # SQLite async engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # 用户/密码模型
│   │   ├── vehicle.py         # 车辆模型
│   │   ├── fuel_record.py     # 加油记录模型
│   │   └── maintenance.py     # 保养记录模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py            # 登录/密码修改 schema
│   │   ├── vehicle.py
│   │   ├── record.py
│   │   ├── maintenance.py
│   │   └── common.py          # 通用响应 schema
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # /api/v1/auth/*
│   │   ├── vehicles.py        # /api/v1/vehicles/*
│   │   ├── records.py         # /api/v1/records/*
│   │   ├── stats.py           # /api/v1/records/stats
│   │   ├── maintenance.py     # /api/v1/maintenance/*
│   │   └── export.py          # /api/v1/export/*
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── record_service.py
│   │   └── stats_service.py   # 油耗计算逻辑
│   ├── tests/
│   │   ├── conftest.py        # pytest fixtures（测试数据库）
│   │   ├── test_auth.py
│   │   ├── test_records.py
│   │   └── test_stats.py
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   ├── requirements.txt
│   ├── Dockerfile              # 后端 Docker 文件
│   └── nginx.conf              # Nginx 配置（生产环境）
├── docker-compose.yml          # Docker Compose 配置（可选，用于开发）
├── Dockerfile                  # 多阶段构建（前端+后端+Nginx）
├── .dockerignore
├── CLAUDE.md
└── PROMPT.md
```

## 数据库设计

### users 表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT NOT NULL,       -- bcrypt 哈希
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### vehicles 表
```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                -- 如 "我的卡罗拉"
    brand TEXT,                        -- 品牌
    model TEXT,                        -- 型号
    plate_number TEXT UNIQUE,          -- 车牌号
    initial_odometer INTEGER DEFAULT 0,-- 初始里程
    fuel_type TEXT DEFAULT '92号汽油',  -- 燃油类型
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### fuel_records 表
```sql
CREATE TABLE fuel_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
    date DATE NOT NULL,                -- 加油日期
    odometer INTEGER NOT NULL,         -- 当前里程
    volume REAL NOT NULL,              -- 加油量（升）
    total_cost REAL NOT NULL,          -- 总金额（元）
    unit_price REAL,                   -- 单价（元/升）
    full_tank BOOLEAN DEFAULT 1,       -- 是否加满
    gas_station TEXT,                  -- 加油站名称
    notes TEXT,                        -- 备注
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### maintenance_records 表
```sql
CREATE TABLE maintenance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
    type TEXT NOT NULL,                -- 保养类型（机油、轮胎、刹车等）
    date DATE NOT NULL,
    odometer INTEGER NOT NULL,
    cost REAL,
    description TEXT,
    next_maintenance_odometer INTEGER, -- 下次保养里程
    next_maintenance_date DATE,        -- 下次保养日期
    is_completed BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API 设计

所有接口统一前缀 `/api/v1`，返回格式：

```json
{"code": 0, "message": "success", "data": {...}}
```

错误时：
```json
{"code": 40001, "message": "密码错误", "data": null}
```

### 认证
| 方法   | 路径                      | 说明         |
| ------ | ------------------------- | ------------ |
| POST   | /api/v1/auth/setup        | 初始化密码   |
| POST   | /api/v1/auth/login        | 密码验证     |
| PUT    | /api/v1/auth/password     | 修改密码     |

认证方式：登录成功返回一个 token（简单 base64 UUID 即可，存 localStorage），后续请求通过 `Authorization: Bearer <token>` 携带。

### 车辆管理
| 方法   | 路径                    | 说明         |
| ------ | ----------------------- | ------------ |
| GET    | /api/v1/vehicles         | 车辆列表     |
| POST   | /api/v1/vehicles         | 添加车辆     |
| PUT    | /api/v1/vehicles/{id}    | 编辑车辆     |
| DELETE | /api/v1/vehicles/{id}    | 删除车辆     |

### 加油记录
| 方法   | 路径                           | 说明              |
| ------ | ------------------------------ | ----------------- |
| GET    | /api/v1/records?vehicle_id=&page=&page_size=&start_date=&end_date= | 记录列表（分页） |
| POST   | /api/v1/records                | 新增记录          |
| PUT    | /api/v1/records/{id}           | 编辑记录          |
| DELETE | /api/v1/records/{id}           | 删除记录          |
| GET    | /api/v1/records/{id}           | 记录详情          |

### 统计
| 方法   | 路径                                | 说明                    |
| ------ | ----------------------------------- | ----------------------- |
| GET    | /api/v1/records/stats?vehicle_id=&period=month | 油耗统计（按月/按年） |
| GET    | /api/v1/records/stats/trend?vehicle_id=&months=6 | 油耗趋势               |
| GET    | /api/v1/records/stats/summary?vehicle_id= | 总览（总花费、总里程等）|

油耗计算逻辑：取连续两次"加满"记录，用 `(后一次里程 - 前一次里程) / 后一次加油量` 计算 L/100km。非连续加满的记录做插值估算。

### 保养
| 方法   | 路径                              | 说明         |
| ------ | --------------------------------- | ------------ |
| GET    | /api/v1/maintenance?vehicle_id=   | 保养列表     |
| POST   | /api/v1/maintenance               | 新增保养     |
| PUT    | /api/v1/maintenance/{id}          | 编辑保养     |
| DELETE | /api/v1/maintenance/{id}          | 删除保养     |
| GET    | /api/v1/maintenance/upcoming?vehicle_id= | 即将到来的保养提醒 |

### 导出
| 方法   | GET                            | 说明             |
| ------ | ------------------------------ | ---------------- |
| GET    | /api/v1/export/csv?vehicle_id=&start_date=&end_date= | 导出 CSV  |
| GET    | /api/v1/export/excel?vehicle_id=&start_date=&end_date= | 导出 Excel |

## UI / UX 设计要求

### 设计原则
1. **移动优先**：以 375px 宽度为基准设计，适配 iPhone/Android 主流机型
2. **操作高效**：加油记录添加流程尽量 3 步内完成（选车 → 填数据 → 提交）
3. **数据可视化**：首页展示关键指标卡片 + 油耗趋势折线图
4. **流畅动效**：页面切换、列表滑动使用 Vant 内置过渡动画

### 颜色方案
- 主色：`#4F46E5`（靛蓝）或 `#2563EB`（蓝）
- 背景：`#F5F7FA`（浅灰）
- 卡片：白色 + 微阴影
- 文字：`#1F2937`（深灰）、`#6B7280`（灰色辅助）
- 强调：`#10B981`（绿色，省油）/ `#EF4444`（红色，费油）

### 页面清单

#### 1. 登录页
- 简洁密码输入框，首次使用引导设置密码
- 背景使用渐变色或汽车相关插画

#### 2. 首页仪表盘
- 顶部：当前选中车辆 + 下拉切换
- 指标卡片行：本次油耗、平均油耗、本月花费、总里程
- 油耗趋势折线图（ECharts，最近 6 个月）
- 最近 3 条加油记录
- 底部 Tab 导航栏

#### 3. 记录列表
- 按时间倒序展示加油记录
- 每条卡片显示：日期、加油站、油量、金额、油耗
- 支持按月份筛选
- 左滑删除（Vant SwipeCell）
- 右下角浮动添加按钮

#### 4. 新增/编辑记录
- 车辆选择（若有多车）
- 日期选择器
- 里程输入（自动带出上次里程供参考）
- 加油量、总金额输入（自动计算单价）
- 是否加满开关
- 加油站选择/输入
- 备注

#### 5. 车辆管理
- 车辆卡片列表
- 添加/编辑/删除车辆
- 每辆车显示：名称、品牌型号、车牌、累计记录数

#### 6. 统计分析
- 时间维度切换：近 3 月 / 近 6 月 / 近 1 年 / 全部
- 月度花费柱状图
- 油耗趋势折线图
- 累计统计汇总表

#### 7. 保养提醒
- 保养记录列表
- 即将到期提醒（里程/日期临近，标红显示）
- 新增保养记录

#### 8. 设置
- 修改密码
- 数据导出（CSV / Excel）
- 关于

### 底部导航
4 个 Tab：首页、记录、统计、我的

## Docker 部署方案

### 设计理念

**一键部署**：使用单个 `Dockerfile` 通过多阶段构建完成前端、后端、Nginx 的完整打包，用户只需执行 `docker build` 和 `docker run` 即可运行整个应用。

### 部署架构

```
┌─────────────────────────────────────────────────┐
│              Docker Container                   │
│  ┌───────────────────────────────────────────┐  │
│  │           Nginx (端口 80)                 │  │
│  │  ┌─────────────────┐  ┌────────────────┐  │  │
│  │  │  静态文件       │  │  /api → 后端   │  │  │
│  │  │  (Vue 打包)     │  │  反向代理      │  │  │
│  │  └─────────────────┘  └───────┬────────┘  │  │
│  └───────────────────────────────────────┼─────┘  │
│                                          │        │
│  ┌───────────────────────────────────────▼─────┐  │
│  │         FastAPI (端口 8000)                │  │
│  │  SQLite 数据库（持久化卷挂载）              │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Dockerfile（多阶段构建）

```dockerfile
# ==================== 阶段 1: 构建前端 ====================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/client

# 复制前端依赖文件
COPY client/package.json client/pnpm-lock.yaml* ./

# 安装 pnpm 并安装依赖
RUN npm install -g pnpm && pnpm install

# 复制前端源码并构建
COPY client/ ./
RUN pnpm build

# ==================== 阶段 2: 准备后端 ====================
FROM python:3.11-slim AS backend-builder

WORKDIR /app/server

# 安装后端依赖
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ==================== 阶段 3: 最终镜像 ====================
FROM python:3.11-slim

WORKDIR /app

# 安装 Nginx 和后端运行依赖
RUN apt-get update && \
    apt-get install -y nginx sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制后端依赖和代码
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY server/ ./server/

# 从前端构建阶段复制静态文件到 Nginx
COPY --from=frontend-builder /app/client/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY docker/nginx.conf /etc/nginx/nginx.conf

# 创建数据目录用于持久化 SQLite 数据库
RUN mkdir -p /app/data && \
    chown -R www-data:www-data /app/data /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动脚本：同时启动 Nginx 和 FastAPI
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### entrypoint.sh

```bash
#!/bin/bash
set -e

# 启动 FastAPI 后端（后台运行）
cd /app/server
# 首次运行：自动初始化数据库
if [ ! -f /app/data/fuel.db ]; then
    echo "Initializing database..."
    python -c "from database import engine; from models import Base; import asyncio; asyncio.run(Base.metadata.create_all(bind=engine))"
fi

# 启动 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 启动 Nginx 前台运行
nginx -g 'daemon off;'
```

### docker/nginx.conf

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 前端静态文件服务
    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Gzip 压缩
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
        gzip_min_length 1000;

        # API 反向代理到 FastAPI
        location /api/ {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Vue Router history 模式支持
        location / {
            try_files $uri $uri/ /index.html;
        }

        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### .dockerignore

```
node_modules
.git
.gitignore
__pycache__
*.pyc
.venv
venv/
.egg-info
dist/
*.log
.env.local
.DS_Store
coverage/
.pytest_cache/
```

### 部署命令

```bash
# 构建镜像
docker build -t fuel-consumption-record:latest .

# 运行容器（数据持久化）
docker run -d \
  --name fuel-record \
  -p 80:80 \
  -v fuel-data:/app/data \
  --restart unless-stopped \
  fuel-consumption-record:latest

# 查看日志
docker logs -f fuel-record

# 备份数据库
docker cp fuel-record:/app/data/fuel.db ./backup-$(date +%Y%m%d).db

# 停止并删除
docker stop fuel-record && docker rm fuel-record
```

### docker-compose.yml（开发环境）

支持前后端独立容器开发，带热重载：

```yaml
services:
  # 前端开发服务（Vite 热重载）
  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile.dev
    volumes:
      - ./client:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    command: pnpm dev --host

  # 后端开发服务（FastAPI 热重载）
  backend:
    build:
      context: ./server
      dockerfile: Dockerfile.dev
    volumes:
      - ./server:/app
      - server-data:/app/data
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:////app/data/fuel.db
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  server-data:

# 使用命令：
# docker compose up -d        # 启动开发环境
# docker compose logs -f      # 查看日志
# docker compose down         # 停止并清理
```

### client/Dockerfile.dev（前端开发镜像）

```dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install

# 开发时挂载源码目录，CMD 由 docker-compose 覆盖
CMD ["pnpm", "dev", "--host"]
```

### server/Dockerfile.dev（后端开发镜像）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建数据目录
RUN mkdir -p /app/data

# 开发时挂载源码目录，CMD 由 docker-compose 覆盖
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 生产部署要点

1. **数据持久化**：必须挂载 `/app/data` 卷，否则容器删除后数据丢失
2. **端口映射**：容器内部 80 端口映射到宿主机任意端口
3. **日志管理**：建议配置 Docker 日志驱动防止日志文件膨胀
4. **数据库备份**：定期执行 `docker cp` 备份 SQLite 文件

## 开发步骤（建议顺序）

请 AI Agent 按以下顺序分步实现，每步完成后验证：

### 第 1 步：项目初始化
- 创建前后端项目结构
- 配置 Vite + Vue 3 + TypeScript + Vant + Tailwind
- 配置 FastAPI + SQLAlchemy + Alembic
- 配置 CORS、Vite proxy

### 第 2 步：后端核心 API
- 实现数据库模型和迁移
- 实现认证模块（setup / login / password change）
- 实现车辆 CRUD
- 实现加油记录 CRUD（含分页、筛选）

### 第 3 步：前端核心框架
- Axios 封装 + 请求拦截器
- Pinia stores
- Vue Router 配置 + 路由守卫
- 底部 Tab 导航栏组件
- 登录页

### 第 4 步：加油记录功能
- 记录列表页
- 新增/编辑记录表单页
- 车辆管理页

### 第 5 步：统计与图表
- 后端统计接口（油耗计算、趋势、汇总）
- 前端统计页 + ECharts 图表

### 第 6 步：保养与导出
- 保养 CRUD + 提醒逻辑
- 数据导出 API
- 保养页面 + 设置页

### 第 7 步：Docker 部署配置
- 创建多阶段 Dockerfile（前端构建 + 后端运行 + Nginx）
- 创建 nginx.conf 配置文件
- 创建 entrypoint.sh 启动脚本
- 创建 .dockerignore 文件
- 创建 docker-compose.yml（开发环境）
- 测试构建和运行

### 第 8 步：优化完善
- 首页仪表盘完善
- 响应式适配
- 动效优化
- 错误处理和边界情况

## 注意事项

1. **前后端分离**：开发时 Vite 配置 proxy 转发 `/api` 到 FastAPI
2. **中文 UI**：所有界面文案使用中文
3. **代码规范**：Python 使用 Ruff 格式化，前端使用 ESLint + Prettier
4. **首次启动**：后端启动时自动创建 SQLite 数据库文件，若 users 表为空则标记为未初始化状态
5. **单用户场景**：不需要注册功能，只需一个管理员密码
6. **不要过度工程**：这是一个个人工具项目，保持代码简洁实用
