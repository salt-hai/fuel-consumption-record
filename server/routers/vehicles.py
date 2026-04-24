from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from models.vehicle import Vehicle
from models.fuel_record import FuelRecord
from models.user import User
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from schemas.common import success_response
from utils.auth import get_current_user, get_user_vehicle

router = APIRouter(prefix="/v1/vehicles", tags=["车辆管理"])

@router.get("/")
async def get_vehicles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的车辆列表"""
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.user_id == current_user.id)
        .order_by(Vehicle.created_at.desc())
    )
    vehicles = result.scalars().all()
    return success_response([VehicleResponse.model_validate(v) for v in vehicles])

@router.post("/")
async def create_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新车辆（关联到当前用户）"""
    vehicle = Vehicle(**data.model_dump(), user_id=current_user.id)
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "添加成功")

@router.put("/{vehicle_id}/")
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新车辆（只能更新自己的车辆）"""
    vehicle = await get_user_vehicle(vehicle_id, current_user, db)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "更新成功")

@router.delete("/{vehicle_id}/")
async def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除车辆（只能删除自己的车辆）"""
    vehicle = await get_user_vehicle(vehicle_id, current_user, db)

    # 删除关联的加油记录
    await db.execute(delete(FuelRecord).where(FuelRecord.vehicle_id == vehicle_id))
    await db.delete(vehicle)
    await db.commit()

    return success_response(message="删除成功")
