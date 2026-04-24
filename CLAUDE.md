# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fuel consumption record app (汽车油耗记录) — a mobile-first web application for tracking vehicle fuel consumption, maintenance, and costs.

## Tech Stack

- **Frontend**: Vue 3 (Composition API, `<script setup>`) + Vite + TypeScript
- **UI Framework**: Mobile-first design, use Tailwind CSS or a mobile-optimized component library (e.g., Vant 4)
- **Backend**: Python FastAPI + SQLite (via SQLAlchemy or aiosqlite)
- **Build**: `pnpm` (frontend), `pip` / `uv` (backend)
- **Deployment**: Docker + Nginx (single multi-stage image)

## Development Commands

### Frontend (`client/`)
```bash
pnpm install          # Install dependencies
pnpm dev              # Start dev server (port 5173)
pnpm build            # Production build
pnpm preview          # Preview production build
pnpm lint             # Lint with ESLint
pnpm type-check       # TypeScript type checking
```

### Backend (`server/`)
```bash
pip install -r requirements.txt   # Or: uv sync
uvicorn main:app --reload         # Start dev server (port 8000)
pytest                            # Run tests
pytest tests/test_fuel.py -k "test_xxx"  # Run single test
```

### Docker (Deployment)
```bash
# ===== 生产环境（单镜像） =====
docker build -t fuel-record:latest .
docker run -d --name fuel-record -p 80:80 -v fuel-data:/app/data --restart unless-stopped fuel-record:latest
docker logs -f fuel-record
docker stop fuel-record && docker rm fuel-record

# ===== 开发环境（Docker Compose） =====
docker compose up -d              # 启动前端+后端（热重载）
docker compose logs -f frontend   # 查看前端日志
docker compose logs -f backend    # 查看后端日志
docker compose down               # 停止并清理

# ===== 数据备份 =====
docker cp fuel-record:/app/data/fuel.db ./backup-$(date +%Y%m%d).db
```

## Architecture

```
fuel-consumption-record/
├── client/                 # Vue 3 frontend (Vite)
│   ├── src/
│   │   ├── views/          # Page components
│   │   ├── components/     # Reusable components
│   │   ├── composables/    # Shared composition functions
│   │   ├── stores/         # Pinia state stores
│   │   ├── api/            # Axios API client modules
│   │   ├── router/         # Vue Router config
│   │   └── utils/          # Utility functions
│   └── ...
├── server/                 # FastAPI backend
│   ├── main.py             # App entry point
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── routers/            # API route modules
│   ├── services/           # Business logic layer
│   ├── database.py         # SQLite connection & session
│   └── tests/
├── docker/                 # Docker 配置
│   ├── nginx.conf          # Nginx 配置（生产）
│   └── entrypoint.sh       # 容器启动脚本
├── Dockerfile              # 多阶段构建（生产）
├── docker-compose.yml      # 开发环境
├── .dockerignore
└── CLAUDE.md
```

**Docker 部署架构**：
- 单个 Dockerfile 多阶段构建（前端 → 后端 → Nginx）
- Nginx 提供静态文件服务 + API 反向代理
- SQLite 数据持久化到挂载卷 `/app/data`

## Key Patterns

- **API**: RESTful, `/api/` prefix with version `/v1/`. JSON responses with consistent `{code, message, data}` envelope.
- **Auth**: Email + password login, returns token. Frontend sends token via `Authorization: Bearer <token>` header.
- **DB Migrations**: Use Alembic for schema changes.
- **State Management**: Pinia stores, one per domain (vehicles, records, auth).
- **Mobile-First**: Design for 375px viewport first. Use Vant 4 components for native app feel. Support responsive up to tablet.
- **Language**: UI in Chinese (zh-CN). Code comments and variable names in English.
- **Docker Dev**: Use `docker compose up` for local development (hot-reload enabled). Build production image with `docker build`.

## Core Features

- Fuel records (date, odometer, amount, volume, price, gas station, notes, full tank flag)
- Fuel consumption calculation using cumulative method (L/100km)
- Multi-vehicle management with user isolation
- Dashboard with charts (ECharts)
- Maintenance records and reminders
- Data export (CSV with UTF-8 BOM, Excel with styling)
- Email/password authentication with token-based sessions

## API Endpoints

**Auth (`/api/v1/auth`)**
- `POST /register` — Register new user
- `POST /login` — Email + password login
- `DELETE /logout/` — Logout (invalidate token)
- `GET /me/` — Get current user info
- `PUT /password/` — Change password

**Vehicles (`/api/v1/vehicles`)**
- `GET /` — List user's vehicles
- `POST /` — Create vehicle
- `PUT /{vehicle_id}/` — Update vehicle
- `DELETE /{vehicle_id}/` — Delete vehicle (and associated records)

**Records (`/api/v1/records`)**
- `GET /` — List records (paginated, filterable)
- `GET /{record_id}/` — Get single record
- `POST /` — Create record
- `PUT /{record_id}/` — Update record
- `DELETE /{record_id}/` — Delete record

**Stats (`/api/v1/stats`)**
- `GET /summary/` — Summary statistics (total cost, distance, avg consumption)
- `GET /monthly/` — Monthly statistics
- `GET /trend/` — Consumption trend

**Maintenance (`/api/v1/maintenance`)**
- `GET ` — List maintenance records
- `GET /upcoming` — Get upcoming maintenance reminders
- `POST ` — Create maintenance record
- `PUT /{record_id}` — Update maintenance record
- `DELETE /{record_id}` — Delete maintenance record

**Export (`/api/v1/export`)**
- `GET /csv` — Export as CSV
- `GET /excel` — Export as Excel
