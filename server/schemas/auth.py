from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码（至少6位）")
    name: str = Field(..., min_length=1, max_length=50, description="用户名")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, description="新密码")


class AuthResponse(BaseModel):
    token: str
    user: dict
