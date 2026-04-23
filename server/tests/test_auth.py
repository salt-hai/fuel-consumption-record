import pytest
from httpx import AsyncClient


class TestAuth:
    """测试认证相关接口"""

    async def test_setup_password(self, client: AsyncClient):
        """测试设置密码"""
        response = await client.post("/api/v1/auth/setup", json={"password": "test123"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "token" in data["data"]

    async def test_setup_twice_should_fail(self, client: AsyncClient):
        """测试重复设置密码应该失败"""
        await client.post("/api/v1/auth/setup", json={"password": "test123"})

        response = await client.post("/api/v1/auth/setup", json={"password": "test456"})
        assert response.status_code == 400

    async def test_login_with_correct_password(self, client: AsyncClient):
        """测试正确密码登录"""
        await client.post("/api/v1/auth/setup", json={"password": "test123"})

        response = await client.post("/api/v1/auth/login", json={"password": "test123"})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "token" in data["data"]

    async def test_login_with_wrong_password(self, client: AsyncClient):
        """测试错误密码登录应该失败"""
        await client.post("/api/v1/auth/setup", json={"password": "test123"})

        response = await client.post("/api/v1/auth/login", json={"password": "wrong"})
        assert response.status_code == 401

    async def test_login_without_setup_should_fail(self, client: AsyncClient):
        """测试未设置密码时登录应该失败"""
        response = await client.post("/api/v1/auth/login", json={"password": "test123"})
        assert response.status_code == 401

    async def test_change_password(self, client: AsyncClient):
        """测试修改密码"""
        await client.post("/api/v1/auth/setup", json={"password": "old123"})

        response = await client.put("/api/v1/auth/password", json={
            "old_password": "old123",
            "new_password": "new123"
        })
        assert response.status_code == 200

        # 验证新密码可以登录
        login_response = await client.post("/api/v1/auth/login", json={"password": "new123"})
        assert login_response.status_code == 200

    async def test_change_password_with_wrong_old_password(self, client: AsyncClient):
        """测试使用错误的旧密码修改密码应该失败"""
        await client.post("/api/v1/auth/setup", json={"password": "test123"})

        response = await client.put("/api/v1/auth/password", json={
            "old_password": "wrong",
            "new_password": "new123"
        })
        assert response.status_code == 400
