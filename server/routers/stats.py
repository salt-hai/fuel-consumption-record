from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db
from models.fuel_record import FuelRecord
from models.vehicle import Vehicle
from models.user import User
from schemas.common import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/v1/stats", tags=["统计分析"])

async def validate_vehicle_for_user(vehicle_id: int, user: User, db: AsyncSession) -> Vehicle:
    """验证车辆属于当前用户"""
    result = await db.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user.id)
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    return vehicle

@router.get("/summary/")
async def get_summary(
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的统计汇总"""
    # 只查询当前用户车辆的记录
    query = select(FuelRecord).join(Vehicle, FuelRecord.vehicle_id == Vehicle.id).where(Vehicle.user_id == current_user.id)

    if vehicle_id:
        # 验证车辆属于当前用户
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        query = query.where(FuelRecord.vehicle_id == vehicle_id)

    result = await db.execute(query)
    records = result.scalars().all()

    if not records:
        return success_response({
            "total_records": 0,
            "total_cost": 0,
            "total_distance": 0,
            "avg_consumption": 0,
            "latest_consumption": 0
        })

    total_cost = sum(r.total_cost for r in records)

    # 计算总里程 (最大里程 - 最小里程)
    min_odometer = min(r.odometer for r in records)
    max_odometer = max(r.odometer for r in records)
    total_distance = max_odometer - min_odometer

    # 计算平均油耗
    consumptions = [r.fuel_consumption for r in records if r.fuel_consumption]
    avg_consumption = sum(consumptions) / len(consumptions) if consumptions else 0

    # 最新油耗
    latest_record = max(records, key=lambda r: r.date)
    latest_consumption = latest_record.fuel_consumption or 0

    return success_response({
        "total_records": len(records),
        "total_cost": round(total_cost, 2),
        "total_distance": total_distance,
        "avg_consumption": round(avg_consumption, 1),
        "latest_consumption": round(latest_consumption, 1)
    })

@router.get("/monthly/")
async def get_monthly_stats(
    vehicle_id: Optional[int] = Query(None),
    period: Optional[str] = Query(None, description="统计周期: month或year"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的月度统计"""
    # 只查询当前用户车辆的记录
    base_query = select(FuelRecord).join(Vehicle, FuelRecord.vehicle_id == Vehicle.id).where(Vehicle.user_id == current_user.id)

    if vehicle_id:
        # 验证车辆属于当前用户
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        base_query = base_query.where(FuelRecord.vehicle_id == vehicle_id)

    query = select(
        func.substr(FuelRecord.date, 1, 7).label('month'),
        func.sum(FuelRecord.total_cost).label('cost'),
        func.sum(FuelRecord.volume).label('volume'),
        func.max(FuelRecord.odometer).label('max_odometer'),
        func.min(FuelRecord.odometer).label('min_odometer')
    ).select_from(base_query.subquery())

    query = query.group_by(func.substr(FuelRecord.date, 1, 7))
    query = query.order_by(func.substr(FuelRecord.date, 1, 7).desc())

    result = await db.execute(query)
    rows = result.all()

    stats = []
    for row in rows:
        distance = row.max_odometer - row.min_odometer if row.max_odometer and row.min_odometer else 0
        consumption = (row.volume / distance * 100) if distance > 0 and row.volume else 0

        stats.append({
            "month": row.month,
            "cost": round(row.cost, 2) if row.cost else 0,
            "volume": round(row.volume, 2) if row.volume else 0,
            "distance": distance,
            "consumption": round(consumption, 1)
        })

    return success_response(stats)

@router.get("/trend/")
async def get_consumption_trend(
    vehicle_id: Optional[int] = Query(None),
    months: int = Query(6, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的油耗趋势"""
    # 只查询当前用户车辆的记录
    query = select(FuelRecord).join(Vehicle, FuelRecord.vehicle_id == Vehicle.id).where(
        Vehicle.user_id == current_user.id,
        FuelRecord.fuel_consumption.isnot(None)
    )

    if vehicle_id:
        # 验证车辆属于当前用户
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        query = query.where(FuelRecord.vehicle_id == vehicle_id)

    query = query.order_by(FuelRecord.date.asc())
    query = query.limit(months)

    result = await db.execute(query)
    records = result.scalars().all()

    trend = [
        {
            "date": r.date,
            "consumption": round(r.fuel_consumption, 1) if r.fuel_consumption else 0
        }
        for r in records
    ]

    return success_response(trend)
