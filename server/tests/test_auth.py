"""测试认证相关接口"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


class TestTokenAuth:
    """测试 Token 认证系统"""

    async def test_register_creates_token(self, client: AsyncClient, db_session):
        """测试注册时创建 token"""
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "token" in data["data"]
        assert data["data"]["user"]["email"] == "test@example.com"

    async def test_register_duplicate_email_should_fail(self, client: AsyncClient):
        """测试重复注册应该失败"""
        await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })

        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password456",
            "name": "Another User"
        })
        assert response.status_code == 400

    async def test_login_returns_token(self, client: AsyncClient):
        """测试登录返回 token"""
        # 先注册
        await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })

        # 再登录
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "token" in data["data"]

    async def test_login_with_wrong_password_should_fail(self, client: AsyncClient):
        """测试错误密码登录应该失败"""
        await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })

        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient):
        """测试获取当前用户"""
        # 注册并获取 token
        reg_response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        token = reg_response.json()["data"]["token"]

        # 使用 token 获取当前用户
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["email"] == "test@example.com"

    async def test_get_current_user_without_token_should_fail(self, client: AsyncClient):
        """测试无 token 获取当前用户应该失败"""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_current_user_with_invalid_token_should_fail(self, client: AsyncClient):
        """测试无效 token 获取当前用户应该失败"""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    async def test_logout_deletes_token(self, client: AsyncClient):
        """测试退出登录删除 token"""
        # 注册并获取 token
        reg_response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        token = reg_response.json()["data"]["token"]

        # 退出登录
        response = await client.delete(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # 后续请求应该失败
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    async def test_change_password(self, client: AsyncClient):
        """测试修改密码"""
        # 注册并获取 token
        reg_response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "oldpassword123",
            "name": "Test User"
        })
        token = reg_response.json()["data"]["token"]

        # 修改密码
        response = await client.put(
            "/api/v1/auth/password",
            json={
                "old_password": "oldpassword123",
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # 用新密码登录
        login_response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "newpassword123"
        })
        assert login_response.status_code == 200

    async def test_change_password_with_wrong_old_password_should_fail(self, client: AsyncClient):
        """测试使用错误的旧密码修改密码应该失败"""
        # 注册并获取 token
        reg_response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        token = reg_response.json()["data"]["token"]

        # 用错误的旧密码修改密码
        response = await client.put(
            "/api/v1/auth/password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

    async def test_change_password_without_token_should_fail(self, client: AsyncClient):
        """测试无 token 修改密码应该失败"""
        response = await client.put("/api/v1/auth/password", json={
            "old_password": "old123",
            "new_password": "new123"
        })
        assert response.status_code == 401
