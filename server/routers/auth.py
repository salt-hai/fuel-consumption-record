from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from database import get_db
from models.user import User
from models.token import Token
from schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest
from schemas.common import success_response
from utils.auth import get_current_user, generate_token, hash_token

router = APIRouter(prefix="/v1/auth", tags=["认证"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_token_from_header(authorization: str = Header(None)) -> str:
    """从 Authorization 头提取 token"""
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]
    return ""

@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
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

    # 创建 token
    token = generate_token()
    token_obj = Token(user_id=user.id, token_hash=hash_token(token))
    db.add(token_obj)
    await db.commit()

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

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    # 创建 token
    token = generate_token()
    token_obj = Token(user_id=user.id, token_hash=hash_token(token))
    db.add(token_obj)
    await db.commit()

    return success_response({
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }, "登录成功")

@router.delete("/logout")
async def logout(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db)
):
    """退出登录 - 删除当前 token"""
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    token_hash = hash_token(token)
    result = await db.execute(select(Token).where(Token.token_hash == token_hash))
    token_obj = result.scalar_one_or_none()

    if token_obj:
        await db.delete(token_obj)
        await db.commit()

    return success_response(message="退出成功")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return success_response({
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    })

@router.put("/password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    if not verify_password(data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    current_user.password_hash = get_password_hash(data.new_password)
    await db.commit()

    return success_response(message="密码修改成功")
