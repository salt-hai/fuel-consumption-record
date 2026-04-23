from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import (
    auth_router,
    vehicles_router,
    records_router,
    stats_router,
    maintenance_router,
    export_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时的清理工作

app = FastAPI(
    title="油耗记录 API",
    description="汽车油耗记录系统后端 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(vehicles_router, prefix="/api")
app.include_router(records_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(maintenance_router, prefix="/api")
app.include_router(export_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "油耗记录 API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
