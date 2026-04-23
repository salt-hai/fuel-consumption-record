import pytest
from httpx import AsyncClient


class TestRecords:
    """测试加油记录接口"""

    async def test_create_record(self, client: AsyncClient):
        """测试创建加油记录"""
        # 先创建车辆
        vehicle_response = await client.post("/api/v1/vehicles", json={
            "name": "测试车",
            "initial_odometer": 1000
        })
        vehicle_id = vehicle_response.json()["data"]["id"]

        # 创建记录
        response = await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-15",
            "odometer": 1500,
            "volume": 40.5,
            "total_cost": 320.5,
            "unit_price": 7.92,
            "full_tank": True,
            "gas_station": "中石化",
            "notes": "测试记录"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["volume"] == 40.5

    async def test_get_records(self, client: AsyncClient):
        """测试获取记录列表"""
        # 创建车辆和记录
        vehicle_response = await client.post("/api/v1/vehicles", json={"name": "测试车"})
        vehicle_id = vehicle_response.json()["data"]["id"]

        await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        response = await client.get("/api/v1/records")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 1
        assert len(data["data"]["items"]) == 1

    async def test_get_records_with_vehicle_filter(self, client: AsyncClient):
        """测试按车辆筛选记录"""
        # 创建两辆车
        v1_response = await client.post("/api/v1/vehicles", json={"name": "车辆1"})
        v1_id = v1_response.json()["data"]["id"]

        v2_response = await client.post("/api/v1/vehicles", json={"name": "车辆2"})
        v2_id = v2_response.json()["data"]["id"]

        # 为车辆1创建记录
        await client.post("/api/v1/records", json={
            "vehicle_id": v1_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        # 为车辆2创建记录
        await client.post("/api/v1/records", json={
            "vehicle_id": v2_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        # 筛选车辆1的记录
        response = await client.get(f"/api/v1/records?vehicle_id={v1_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 1

    async def test_update_record(self, client: AsyncClient):
        """测试更新记录"""
        # 创建车辆和记录
        vehicle_response = await client.post("/api/v1/vehicles", json={"name": "测试车"})
        vehicle_id = vehicle_response.json()["data"]["id"]

        record_response = await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })
        record_id = record_response.json()["data"]["id"]

        # 更新记录
        response = await client.put(f"/api/v1/records/{record_id}", json={
            "volume": 45.5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["volume"] == 45.5

    async def test_delete_record(self, client: AsyncClient):
        """测试删除记录"""
        # 创建车辆和记录
        vehicle_response = await client.post("/api/v1/vehicles", json={"name": "测试车"})
        vehicle_id = vehicle_response.json()["data"]["id"]

        record_response = await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })
        record_id = record_response.json()["data"]["id"]

        # 删除记录
        response = await client.delete(f"/api/v1/records/{record_id}")
        assert response.status_code == 200

        # 验证删除
        records_response = await client.get("/api/v1/records")
        assert records_response.json()["data"]["total"] == 0

    async def test_fuel_consumption_calculation(self, client: AsyncClient):
        """测试油耗计算"""
        # 创建车辆
        vehicle_response = await client.post("/api/v1/vehicles", json={
            "name": "测试车",
            "initial_odometer": 1000
        })
        vehicle_id = vehicle_response.json()["data"]["id"]

        # 第一次加满
        await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-01-01",
            "odometer": 1000,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        # 第二次加满 (行驶了500公里，加了40L)
        # 油耗 = 40 / 500 * 100 = 8 L/100km
        response = await client.post("/api/v1/records", json={
            "vehicle_id": vehicle_id,
            "date": "2024-02-01",
            "odometer": 1500,
            "volume": 40,
            "total_cost": 300,
            "full_tank": True
        })

        data = response.json()
        assert data["data"]["fuel_consumption"] == pytest.approx(8.0, 0.1)
