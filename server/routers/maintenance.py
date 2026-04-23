from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from database import get_db
from models.maintenance import MaintenanceRecord
from models.vehicle import Vehicle
from schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse
from schemas.common import success_response

router = APIRouter(prefix="/v1/maintenance", tags=["保养管理"])

@router.get("")
async def get_maintenance_records(
    vehicle_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(MaintenanceRecord)

    if vehicle_id:
        query = query.where(MaintenanceRecord.vehicle_id == vehicle_id)

    query = query.order_by(MaintenanceRecord.date.desc())
    result = await db.execute(query)
    records = result.scalars().all()

    return success_response([MaintenanceResponse.model_validate(r) for r in records])

@router.get("/upcoming")
async def get_upcoming_maintenance(
    vehicle_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取即将到来的保养提醒"""
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    query = select(MaintenanceRecord).where(
        MaintenanceRecord.is_completed == False
    )

    if vehicle_id:
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
async def create_maintenance(data: MaintenanceCreate, db: AsyncSession = Depends(get_db)):
    # 验证车辆存在
    result = await db.execute(select(Vehicle).where(Vehicle.id == data.vehicle_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="车辆不存在")

    record = MaintenanceRecord(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return success_response(MaintenanceResponse.model_validate(record), "添加成功")

@router.put("/{record_id}")
async def update_maintenance(
    record_id: int,
    data: MaintenanceUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(MaintenanceRecord).where(MaintenanceRecord.id == record_id))
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
async def delete_maintenance(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MaintenanceRecord).where(MaintenanceRecord.id == record_id))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()

    return success_response(message="删除成功")
