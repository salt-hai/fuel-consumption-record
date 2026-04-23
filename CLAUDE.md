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

- **API**: RESTful, `/api/v1/` prefix. JSON responses with consistent `{code, message, data}` envelope.
- **Auth**: Simple password-based. Backend stores a hashed password; frontend sends it with each request via `Authorization` header.
- **DB Migrations**: Use Alembic for schema changes.
- **State Management**: Pinia stores, one per domain (vehicles, records, auth).
- **Mobile-First**: Design for 375px viewport first. Use Vant 4 components for native app feel. Support responsive up to tablet.
- **Language**: UI in Chinese (zh-CN). Code comments and variable names in English.
- **Docker Dev**: Use `docker compose up` for local development (hot-reload enabled). Build production image with `docker build`.

## Core Features

- Fuel records (date, odometer, amount, volume, price, gas station, notes)
- Fuel consumption calculation (L/100km)
- Multi-vehicle management
- Dashboard with charts (ECharts)
- Maintenance reminders
- Data export (CSV/Excel)
- Simple password authentication

## API Endpoints

- `POST /api/v1/auth/login` — Verify password, return token
- `PUT /api/v1/auth/password` — Change password
- `CRUD /api/v1/vehicles` — Vehicle management
- `CRUD /api/v1/records` — Fuel records
- `GET /api/v1/records/stats` — Consumption statistics
- `GET /api/v1/maintenance` — Maintenance reminders
- `GET /api/v1/export` — Export data
