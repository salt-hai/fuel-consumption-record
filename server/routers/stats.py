from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
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


async def get_all_records(
    db: AsyncSession,
    vehicle_id: Optional[int],
    current_user: User
) -> List[FuelRecord]:
    """获取用户所有加油记录，按日期和里程排序"""
    query = select(FuelRecord).join(Vehicle, FuelRecord.vehicle_id == Vehicle.id).where(
        Vehicle.user_id == current_user.id
    )

    if vehicle_id:
        await validate_vehicle_for_user(vehicle_id, current_user, db)
        query = query.where(FuelRecord.vehicle_id == vehicle_id)

    query = query.order_by(FuelRecord.odometer.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


def calculate_consumption_for_month(
    records: List[FuelRecord],
    year: int,
    month: int,
    overall_consumption_rate: float
) -> Tuple[float, float, float, float]:
    """
    计算指定月份的统计数据

    使用混合方法：
    1. 对于该月内完整的加满周期，用累积法准确计算
    2. 对于不完整的周期（首尾），用整体油耗率估算

    overall_consumption_rate: 整体油耗率 (L/100km)
    """
    month_prefix = f"{year}-{month:02d}"

    # 找出所有加满记录及其位置
    full_tank_indices = [i for i, r in enumerate(records) if r.full_tank]

    total_cost = 0.0
    total_volume = 0.0
    total_distance_in_month = 0.0
    estimated_fuel_used = 0.0  # 该月实际消耗的油量（用于计算油耗）

    # 找出该月第一条和最后一条记录的索引
    month_first_idx = None
    month_last_idx = None
    for i, r in enumerate(records):
        if r.date.startswith(month_prefix):
            if month_first_idx is None:
                month_first_idx = i
            month_last_idx = i

    if month_first_idx is None:
        return 0, 0, 0, 0  # 该月没有记录

    # 计算该月里程范围
    first_record = records[month_first_idx]
    last_record = records[month_last_idx]
    month_odometer_start = first_record.odometer
    month_odometer_end = last_record.odometer

    # 计算该月总花费和总油量（加油量，不是消耗量）
    for i in range(month_first_idx, month_last_idx + 1):
        r = records[i]
        total_cost += r.total_cost
        total_volume += r.volume

    total_distance_in_month = month_odometer_end - month_odometer_start

    # 计算该月实际消耗的油量
    # 方法：找出该月内所有"完整加满周期"
    for idx in full_tank_indices:
        record = records[idx]

        if idx == 0:
            continue  # 首次加满，需要特殊处理

        prev_record = records[idx - 1]

        # 检查这个加满周期是否与当前月相关
        cycle_start_odo = prev_record.odometer
        cycle_end_odo = record.odometer

        # 计算该周期在当前月份内的里程
        month_start = max(cycle_start_odo, month_odometer_start)
        month_end = min(cycle_end_odo, month_odometer_end)
        distance_in_month = max(0, month_end - month_start)

        if distance_in_month <= 0:
            continue

        # 获取这个周期的总油量
        cycle_volume = sum(
            r.volume for r in records
            if cycle_start_odo < r.odometer <= cycle_end_odo
        )

        # 计算油耗率
        cycle_distance = cycle_end_odo - cycle_start_odo
        consumption_rate = (cycle_volume / cycle_distance) * 100 if cycle_distance > 0 else 0

        # 该周期在当前月消耗的油量
        fuel_in_month = (distance_in_month / 100) * consumption_rate
        estimated_fuel_used += fuel_in_month

    # 如果没有完整周期，用整体油耗率估算
    if estimated_fuel_used == 0 and total_distance_in_month > 0:
        estimated_fuel_used = (total_distance_in_month / 100) * overall_consumption_rate

    # 处理边界：如果该月首尾有未覆盖的里程段
    # 找出该月第一个完整周期的起点
    first_full_cycle_start = None
    for idx in full_tank_indices:
        if idx > 0:
            prev_idx = idx - 1
            if records[prev_idx].odometer <= month_odometer_end:
                first_full_cycle_start = records[prev_idx].odometer
                break

    # 处理月初未覆盖部分
    if first_full_cycle_start and first_full_cycle_start > month_odometer_start:
        uncovered_start = month_odometer_start
        uncovered_end = min(first_full_cycle_start, month_odometer_end)
        if uncovered_end > uncovered_start:
            uncovered_dist = uncovered_end - uncovered_start
            estimated_fuel_used += (uncovered_dist / 100) * overall_consumption_rate

    # 计算平均油耗
    avg_consumption = (estimated_fuel_used / total_distance_in_month * 100) if total_distance_in_month > 0 else 0

    return total_cost, total_volume, total_distance_in_month, avg_consumption


@router.get("/summary/")
async def get_summary(
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的统计汇总"""
    records = await get_all_records(db, vehicle_id, current_user)

    if not records:
        return success_response({
            "total_records": 0,
            "total_cost": 0,
            "total_distance": 0,
            "avg_consumption": 0,
            "latest_consumption": 0,
            "avg_cost_per_km": 0
        })

    total_cost = sum(r.total_cost for r in records)
    total_volume = sum(r.volume for r in records)

    # 计算总里程
    min_odometer = min(r.odometer for r in records)
    max_odometer = max(r.odometer for r in records)
    total_distance = max_odometer - min_odometer

    # 计算整体平均油耗
    overall_consumption_rate = (total_volume / total_distance * 100) if total_distance > 0 else 0

    # 获取最新加满记录的油耗
    latest_consumption = overall_consumption_rate
    for r in reversed(records):
        if r.full_tank and r.fuel_consumption is not None:
            latest_consumption = r.fuel_consumption
            break

    # 平均油费 (元/公里)
    avg_cost_per_km = round(total_cost / total_distance, 2) if total_distance > 0 else 0

    return success_response({
        "total_records": len(records),
        "total_cost": round(total_cost, 2),
        "total_distance": total_distance,
        "avg_consumption": round(overall_consumption_rate, 1),
        "latest_consumption": round(latest_consumption, 1),
        "avg_cost_per_km": avg_cost_per_km
    })


@router.get("/monthly/")
async def get_monthly_stats(
    vehicle_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的月度统计"""
    records = await get_all_records(db, vehicle_id, current_user)

    if not records:
        return success_response([])

    # 计算整体油耗率，用于估算不完整周期
    total_volume = sum(r.volume for r in records)
    min_odometer = min(r.odometer for r in records)
    max_odometer = max(r.odometer for r in records)
    total_distance = max_odometer - min_odometer
    overall_consumption_rate = (total_volume / total_distance * 100) if total_distance > 0 else 0

    # 获取所有月份
    months = set()
    for r in records:
        months.add(r.date[:7])

    stats = []
    for month_str in sorted(months, reverse=True):
        year = int(month_str[:4])
        month = int(month_str[5:7])

        cost, volume, distance, consumption = calculate_consumption_for_month(
            records, year, month, overall_consumption_rate
        )

        stats.append({
            "month": month_str,
            "cost": round(cost, 2),
            "volume": round(volume, 2),
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
    """获取当前用户的油耗趋势（按月统计）"""
    records = await get_all_records(db, vehicle_id, current_user)

    if not records:
        return success_response([])

    # 计算整体油耗率
    total_volume = sum(r.volume for r in records)
    min_odometer = min(r.odometer for r in records)
    max_odometer = max(r.odometer for r in records)
    total_distance = max_odometer - min_odometer
    overall_consumption_rate = (total_volume / total_distance * 100) if total_distance > 0 else 0

    # 获取所有月份
    all_months = set(r.date[:7] for r in records)
    sorted_months = sorted(all_months, reverse=True)[:months]

    trend = []
    for month_str in reversed(sorted_months):
        year = int(month_str[:4])
        month = int(month_str[5:7])

        _, _, _, consumption = calculate_consumption_for_month(records, year, month, overall_consumption_rate)

        trend.append({
            "date": month_str,
            "consumption": round(consumption, 1)
        })

    return success_response(trend)
