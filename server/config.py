from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置

    支持通过环境变量或 .env 文件配置
    优先级: 环境变量 > .env 文件 > 默认值
    """

    # ===== 数据库配置 =====
    DATABASE_URL: str = "sqlite+aiosqlite:///./fuel.db"

    # ===== JWT 认证配置 =====
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # ===== API 文档配置 =====
    # 是否显示 Swagger UI (ReDoc)
    DOCS_ENABLED: bool = True
    # 是否显示 OpenAPI schema (JSON)
    OPENAPI_ENABLED: bool = True
    # API 文档路径
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    # ===== 应用功能开关 =====
    # 是否启用用户注册（生产环境可关闭）
    REGISTRATION_ENABLED: bool = True
    # 邮箱白名单（逗号分隔，空表示不限制）
    # 示例: user1@example.com,user2@example.com 或 @example.com（允许整个域名）
    EMAIL_WHITELIST: str = ""
    # 是否启用数据导出功能
    EXPORT_ENABLED: bool = True
    # 是否启用保养提醒功能
    MAINTENANCE_ENABLED: bool = True

    # ===== 安全配置 =====
    # 是否启用 CORS（生产环境建议限制具体域名）
    CORS_ENABLED: bool = True
    # 允许的 CORS 源（逗号分隔，* 表示允许所有）
    CORS_ORIGINS: str = "*"
    # 是否启用请求限流
    RATE_LIMIT_ENABLED: bool = False

    # ===== 调试配置 =====
    # 调试模式（生产环境设为 False）
    DEBUG: bool = False
    # 是否显示详细错误信息
    SHOW_DETAILED_ERRORS: bool = False

    # ===== 维护模式 =====
    # 是否开启维护模式（开启后只返回维护信息）
    MAINTENANCE_MODE: bool = False
    # 维护提示信息
    MAINTENANCE_MESSAGE: str = "系统维护中，请稍后访问"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()


def get_docs_config(docs_enabled: bool = True) -> dict:
    """获取 API 文档配置"""
    if not docs_enabled:
        return {"docs_url": None, "redoc_url": None, "openapi_url": None}
    return {
        "docs_url": settings.DOCS_URL,
        "redoc_url": settings.REDOC_URL,
        "openapi_url": settings.OPENAPI_URL if settings.OPENAPI_ENABLED else None,
    }


def get_cors_origins() -> list[str]:
    """解析 CORS 允许的源"""
    if not settings.CORS_ENABLED:
        return []
    origins = settings.CORS_ORIGINS.strip()
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def get_email_whitelist() -> list[str]:
    """解析邮箱白名单

    支持两种格式：
    1. 完整邮箱: user@example.com
    2. 域名通配符: @example.com (允许该域名下所有邮箱)

    返回格式: ["user@example.com", "@example.com"]
    """
    if not settings.EMAIL_WHITELIST:
        return []

    whitelist = []
    for item in settings.EMAIL_WHITELIST.split(","):
        item = item.strip()
        if item:
            # 自动添加 @ 前缀（如果用户只写了域名）
            if not item.startswith("@") and "@" not in item:
                item = f"@{item}"
            whitelist.append(item)
    return whitelist


def is_email_allowed(email: str) -> bool:
    """检查邮箱是否在白名单中

    Args:
        email: 待检查的邮箱地址

    Returns:
        True 如果邮箱在白名单中或白名单为空，False 否则
    """
    whitelist = get_email_whitelist()
    if not whitelist:
        return True

    email_lower = email.lower()

    for allowed in whitelist:
        allowed_lower = allowed.lower()
        # 域名通配符匹配
        if allowed_lower.startswith("@"):
            if email_lower.endswith(allowed_lower):
                return True
        # 完整邮箱匹配
        elif email_lower == allowed_lower:
            return True

    return False
