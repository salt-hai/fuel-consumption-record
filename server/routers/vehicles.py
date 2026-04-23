from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from database import get_db
from models.vehicle import Vehicle
from models.fuel_record import FuelRecord
from schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from schemas.common import success_response

router = APIRouter(prefix="/v1/vehicles", tags=["车辆管理"])

@router.get("")
async def get_vehicles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).order_by(Vehicle.created_at.desc()))
    vehicles = result.scalars().all()
    return success_response([VehicleResponse.model_validate(v) for v in vehicles])

@router.post("")
async def create_vehicle(data: VehicleCreate, db: AsyncSession = Depends(get_db)):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "添加成功")

@router.put("/{vehicle_id}")
async def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(vehicle, key, value)

    await db.commit()
    await db.refresh(vehicle)
    return success_response(VehicleResponse.model_validate(vehicle), "更新成功")

@router.delete("/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")

    await db.execute(delete(FuelRecord).where(FuelRecord.vehicle_id == vehicle_id))
    await db.delete(vehicle)
    await db.commit()

    return success_response(message="删除成功")
