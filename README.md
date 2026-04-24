# 汽车油耗记录系统

一个移动优先的汽车油耗记录 Web 应用，支持多车辆管理、加油记录、油耗统计、保养提醒等功能。

## 功能特性

- 🔐 邮箱密码认证 + Token 会话
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
- SQLite (aiosqlite)
- bcrypt（密码加密）
- openpyxl（Excel 导出）

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

## 配置说明

后端通过环境变量或 `.env` 文件配置，主要配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./fuel.db` | 数据库连接 |
| `SECRET_KEY` | - | JWT 密钥（生产环境必须修改） |
| `DOCS_ENABLED` | `true` | 是否启用 API 文档 |
| `REGISTRATION_ENABLED` | `true` | 是否允许用户注册 |
| `EXPORT_ENABLED` | `true` | 是否启用数据导出功能 |
| `MAINTENANCE_ENABLED` | `true` | 是否启用保养提醒功能 |
| `CORS_ENABLED` | `true` | 是否启用 CORS |
| `CORS_ORIGINS` | `*` | 允许的跨域源 |
| `MAINTENANCE_MODE` | `false` | 维护模式开关 |
| `DEBUG` | `false` | 调试模式 |

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

### API 端点列表

#### 认证 (`/api/v1/auth`)
| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/register` | 注册新用户 |
| POST | `/login` | 邮箱+密码登录 |
| DELETE | `/logout/` | 退出登录 |
| GET | `/me/` | 获取当前用户信息 |
| PUT | `/password/` | 修改密码 |

#### 车辆管理 (`/api/v1/vehicles`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 获取当前用户的车辆列表 |
| POST | `/` | 创建新车辆 |
| PUT | `/{vehicle_id}/` | 更新车辆信息 |
| DELETE | `/{vehicle_id}/` | 删除车辆（含关联记录） |

#### 加油记录 (`/api/v1/records`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 获取加油记录列表（支持分页、筛选） |
| GET | `/{record_id}/` | 获取单条记录详情 |
| POST | `/` | 创建加油记录 |
| PUT | `/{record_id}/` | 更新记录 |
| DELETE | `/{record_id}/` | 删除记录 |

#### 统计分析 (`/api/v1/stats`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/summary/` | 统计汇总（总花费、里程、平均油耗） |
| GET | `/monthly/` | 月度统计 |
| GET | `/trend/` | 油耗趋势 |

#### 保养管理 (`/api/v1/maintenance`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `` | 获取保养记录列表 |
| GET | `/upcoming` | 获取即将到来的保养提醒 |
| POST | `` | 创建保养记录 |
| PUT | `/{record_id}` | 更新保养记录 |
| DELETE | `/{record_id}` | 删除保养记录 |

#### 数据导出 (`/api/v1/export`)
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/csv` | 导出 CSV 格式 |
| GET | `/excel` | 导出 Excel 格式 |

### API 响应格式

所有 API 响应采用统一格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 认证方式

- 邮箱 + 密码登录，返回 Token
- 后续请求通过 `Authorization: Bearer <token>` 头携带认证信息

## 数据备份

```bash
# 备份 SQLite 数据库
docker cp fuel-record:/app/data/fuel.db ./backup-$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backup.db fuel-record:/app/data/fuel.db
```

## 许可证

MIT License
