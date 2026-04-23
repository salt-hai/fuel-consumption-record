from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database import get_db
from models.fuel_record import FuelRecord
from models.vehicle import Vehicle
from schemas.record import RecordCreate, RecordUpdate, RecordResponse, RecordListResponse
from schemas.common import success_response

router = APIRouter(prefix="/v1/records", tags=["加油记录"])

async def calculate_fuel_consumption(
    db: AsyncSession,
    vehicle_id: int,
    current_odometer: int,
) -> Optional[float]:
    """
    计算油耗 (L/100km) - 国际标准累积法

    从上次加满到本次加满之间：
    - 累积加油量 = Σ(中间所有记录的 volume，包括本次)
    - 累积里程 = 本次里程 - 上次加满里程
    - 油耗 = 累积加油量 / 累积里程 × 100
    """
    # 查找上一次加满的记录
    result = await db.execute(
        select(FuelRecord)
        .where(
            and_(
                FuelRecord.vehicle_id == vehicle_id,
                FuelRecord.full_tank == True,
                FuelRecord.odometer < current_odometer
            )
        )
        .order_by(FuelRecord.odometer.desc())
        .limit(1)
    )
    prev_record = result.scalar_one_or_none()

    if not prev_record:
        return None

    # 计算累积里程
    distance = current_odometer - prev_record.odometer
    if distance <= 0:
        return None

    # 查询两次加满之间的所有记录（不包括上次加满，包括本次加满后的记录）
    result = await db.execute(
        select(FuelRecord)
        .where(
            and_(
                FuelRecord.vehicle_id == vehicle_id,
                FuelRecord.odometer > prev_record.odometer,
                FuelRecord.odometer <= current_odometer
            )
        )
    )
    intermediate_records = result.scalars().all()

    # 累积加油量（所有中间记录 + 本次记录的 volume）
    # 注意：本次记录还没保存，所以需要额外计算
    total_volume = sum(r.volume for r in intermediate_records)

    # 计算油耗
    return (total_volume / distance) * 100

@router.get("", response_model=RecordListResponse)
async def get_records(
    vehicle_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(FuelRecord)

    if vehicle_id:
        query = query.where(FuelRecord.vehicle_id == vehicle_id)
    if start_date:
        query = query.where(FuelRecord.date >= start_date)
    if end_date:
        query = query.where(FuelRecord.date <= end_date)

    # 获取总数
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # 分页查询
    query = query.order_by(FuelRecord.date.desc(), FuelRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    records = result.scalars().all()

    return RecordListResponse(
        items=[RecordResponse.model_validate(r) for r in records],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{record_id}", response_model=RecordResponse)
async def get_record(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuelRecord).where(FuelRecord.id == record_id))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return RecordResponse.model_validate(record)

@router.post("", response_model=RecordResponse)
async def create_record(data: RecordCreate, db: AsyncSession = Depends(get_db)):
    # 验证车辆存在
    result = await db.execute(select(Vehicle).where(Vehicle.id == data.vehicle_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="车辆不存在")

    record = FuelRecord(**data.model_dump())

    # 计算油耗（累积法）
    if record.full_tank:
        record.fuel_consumption = await calculate_fuel_consumption(
            db, record.vehicle_id, record.odometer
        )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return RecordResponse.model_validate(record)

@router.put("/{record_id}", response_model=RecordResponse)
async def update_record(
    record_id: int,
    data: RecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(FuelRecord).where(FuelRecord.id == record_id))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    # 重新计算油耗（累积法）
    if record.full_tank:
        record.fuel_consumption = await calculate_fuel_consumption(
            db, record.vehicle_id, record.odometer
        )

    await db.commit()
    await db.refresh(record)

    return RecordResponse.model_validate(record)

@router.delete("/{record_id}")
async def delete_record(record_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FuelRecord).where(FuelRecord.id == record_id))
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    await db.delete(record)
    await db.commit()

    return success_response(message="删除成功")
