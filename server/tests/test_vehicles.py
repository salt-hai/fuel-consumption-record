import pytest
from httpx import AsyncClient


class TestVehicles:
    """测试车辆管理接口"""

    async def test_create_vehicle(self, client: AsyncClient):
        """测试创建车辆"""
        response = await client.post("/api/v1/vehicles", json={
            "name": "我的车",
            "brand": "丰田",
            "model": "卡罗拉",
            "plate_number": "京A12345",
            "initial_odometer": 1000,
            "fuel_type": "92号汽油"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "我的车"

    async def test_get_vehicles(self, client: AsyncClient):
        """测试获取车辆列表"""
        # 先创建两辆车
        await client.post("/api/v1/vehicles", json={"name": "车辆1"})
        await client.post("/api/v1/vehicles", json={"name": "车辆2"})

        response = await client.get("/api/v1/vehicles")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 2

    async def test_update_vehicle(self, client: AsyncClient):
        """测试更新车辆"""
        create_response = await client.post("/api/v1/vehicles", json={"name": "原名称"})
        vehicle_id = create_response.json()["data"]["id"]

        response = await client.put(f"/api/v1/vehicles/{vehicle_id}", json={
            "name": "新名称"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "新名称"

    async def test_delete_vehicle(self, client: AsyncClient):
        """测试删除车辆"""
        create_response = await client.post("/api/v1/vehicles", json={"name": "待删除"})
        vehicle_id = create_response.json()["data"]["id"]

        response = await client.delete(f"/api/v1/vehicles/{vehicle_id}")
        assert response.status_code == 200

        # 验证删除后获取不到
        get_response = await client.get("/api/v1/vehicles")
        assert len(get_response.json()["data"]) == 0

    async def test_delete_vehicle_with_records_should_delete_records(self, client: AsyncClient):
        """测试删除车辆时应该同时删除关联的加油记录"""
        # 创建车辆
        vehicle_response = await client.post("/api/v1/vehicles", json={"name": "测试车"})
        vehicle_id = vehicle_response.json()["data"]["id"]

        # 创建加油记录
        await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        # 删除车辆
        await client.delete(f"/api/v1/vehicles/{vehicle_id}")

        # 验证记录也被删除
        records_response = await client.get("/api/v1/records")
        assert len(records_response.json()["data"]["items"]) == 0
