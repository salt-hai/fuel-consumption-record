from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from models.maintenance import MaintenanceRecord
from models.vehicle import Vehicle
from models.user import User
from schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse
from schemas.common import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/v1/maintenance", tags=["保养管理"])

async def validate_vehicle_for_user(vehicle_id: int, user: User, db: AsyncSession) -> Vehicle:
    """验证车辆属于当前用户"""
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return vehicle

@router.get("")
async def get_maintenance_records(
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的保养记录"""
    query = select(MaintenanceRecord).join(Vehicle, MaintenanceRecord.vehicle_id == Vehicle.id).where(Vehicle.user_id == current_user.id)

    if vehicle_id:
        # 验证车辆属于当前用户
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        query = query.where(MaintenanceRecord.vehicle_id == vehicle_id)

    query = query.order_by(MaintenanceRecord.date.desc())
    result = await db.execute(query)
    records = result.scalars().all()

    return success_response([MaintenanceResponse.model_validate(r) for r in records])

@router.get("/upcoming")
async def get_upcoming_maintenance(
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户即将到来的保养提醒"""
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    # 只查询当前用户车辆的保养记录
    query = select(MaintenanceRecord).join(Vehicle, MaintenanceRecord.vehicle_id == Vehicle.id).where(
        Vehicle.user_id == current_user.id,
        MaintenanceRecord.is_completed == False
    )

    if vehicle_id:
        # 验证车辆属于当前用户
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        query = query.where(MaintenanceRecord.vehicle_id == vehicle_id)

    result = await db.execute(query)
    all_records = result.scalars().all()

    upcoming = []
    for r in all_records:
        if r.next_maintenance_date and r.next_maintenance_date < today:
            upcoming.append(r)
        # 可以添加更多提醒逻辑，比如里程临近

    return success_response([MaintenanceResponse.model_validate(r) for r in upcoming])

@router.post("")
async def create_maintenance(
    data: MaintenanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建保养记录（只能添加到自己的车辆）"""
    # 验证车辆属于当前用户
    vehicle = await validate_vehicle_for_user(data.vehicle_id, current_user, db)

    record = MaintenanceRecord(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(MaintenanceResponse.model_validate(record), "添加成功")

@router.put("/{record_id}")
async def update_maintenance(
    record_id: int,
    data: MaintenanceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新保养记录（只能更新自己的记录）"""
    # 通过车辆关联验证用户
    query = select(MaintenanceRecord).join(Vehicle, MaintenanceRecord.vehicle_id == Vehicle.id).where(
        MaintenanceRecord.id == record_id,
        Vehicle.user_id == current_user.id
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)

    return success_response(MaintenanceResponse.model_validate(record), "更新成功")

@router.delete("/{record_id}")
async def delete_maintenance(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除保养记录（只能删除自己的记录）"""
    # 通过车辆关联验证用户
    query = select(MaintenanceRecord).join(Vehicle, MaintenanceRecord.vehicle_id == Vehicle.id).where(
        MaintenanceRecord.id == record_id,
        Vehicle.user_id == current_user.id
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()

    return success_response(message="删除成功")
