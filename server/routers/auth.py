from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from database import get_db
from models.user import User
from schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest
from schemas.common import success_response

router = APIRouter(prefix="/v1/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token() -> str:
    import uuid
    import base64
    token = str(uuid.uuid4())
    return base64.b64encode(token.encode()).decode()


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        name=data.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token()
    return success_response({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }, "注册成功")


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """邮箱+密码登录"""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    token = create_token()
    return success_response({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }, "登录成功")


@router.put("/password")
async def change_password(data: ChangePasswordRequest, db: AsyncSession = Depends(get_db)):
    """修改密码"""
    # 注意：这里需要从 token 中获取用户信息，暂时简化处理
    # 实际应该从依赖注入的当前用户获取

    # 这里暂时跳过修改密码功能，因为需要实现 token 验证中间件
    raise HTTPException(status_code=501, detail="功能开发中")


@router.get("/me")
async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    """获取当前用户信息（基于 token）"""
    # TODO: 实现基于 token 的用户验证
    # 暂时返回未实现
    raise HTTPException(status_code=501, detail="功能开发中")
