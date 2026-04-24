from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Callable

from config import settings, get_docs_config, get_cors_origins
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


# 获取文档配置
docs_config = get_docs_config(settings.DOCS_ENABLED)

app = FastAPI(
    title="油耗记录 API",
    description="汽车油耗记录系统后端 API",
    version="1.0.0",
    lifespan=lifespan,
    **docs_config,
)


# 维护模式中间件
@app.middleware("http")
async def maintenance_middleware(request: Request, call_next: Callable):
    if settings.MAINTENANCE_MODE:
        # 健康检查端点始终可用
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        # API 文档在维护模式下也可访问（如果启用）
        if settings.DOCS_ENABLED and request.url.path.startswith(settings.DOCS_URL):
            return await call_next(request)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "code": 503,
                "message": settings.MAINTENANCE_MESSAGE,
                "data": None
            }
        )
    return await call_next(request)


# CORS 配置
if settings.CORS_ENABLED:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(vehicles_router, prefix="/api")
app.include_router(records_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
if settings.MAINTENANCE_ENABLED:
    app.include_router(maintenance_router, prefix="/api")
if settings.EXPORT_ENABLED:
    app.include_router(export_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "油耗记录 API",
        "version": "1.0.0",
        "docs": settings.DOCS_URL if settings.DOCS_ENABLED else None,
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "maintenance": settings.MAINTENANCE_MODE}


# 全局异常处理
if settings.SHOW_DETAILED_ERRORS:
    # 开发环境：显示详细错误
    pass
else:
    # 生产环境：隐藏详细错误信息
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "服务器内部错误",
                "data": None
            }
        )
