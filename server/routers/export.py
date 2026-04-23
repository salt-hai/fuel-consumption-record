from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import csv
import io
from database import get_db
from models.fuel_record import FuelRecord
from models.vehicle import Vehicle

router = APIRouter(prefix="/v1/export", tags=["数据导出"])

async def get_export_data(
    vehicle_id: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    db: AsyncSession
):
    query = select(FuelRecord)

    if vehicle_id:
        query = query.where(FuelRecord.vehicle_id == vehicle_id)
    if start_date:
        query = query.where(FuelRecord.date >= start_date)
    if end_date:
        query = query.where(FuelRecord.date <= end_date)

    query = query.order_by(FuelRecord.date.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/csv")
async def export_csv(
    vehicle_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    records = await get_export_data(vehicle_id, start_date, end_date, db)

    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow(["日期", "里程(km)", "加油量(L)", "总金额(元)", "单价(元/L)", "是否加满", "加油站", "油耗(L/100km)", "备注"])

    # 写入数据
    for r in records:
        writer.writerow([
            r.date,
            r.odometer,
            r.volume,
            r.total_cost,
            r.unit_price or "",
            "是" if r.full_tank else "否",
            r.gas_station or "",
            f"{r.fuel_consumption:.1f}" if r.fuel_consumption else "",
            r.notes or ""
        ])

    output.seek(0)
    filename = f"fuel_records_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),  # UTF-8 BOM for Excel
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/excel")
async def export_excel(
    vehicle_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill

    records = await get_export_data(vehicle_id, start_date, end_date, db)

    wb = Workbook()
    ws = wb.active
    ws.title = "加油记录"

    # 表头
    headers = ["日期", "里程(km)", "加油量(L)", "总金额(元)", "单价(元/L)", "是否加满", "加油站", "油耗(L/100km)", "备注"]
    ws.append(headers)

    # 表头样式
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    # 数据行
    for r in records:
        ws.append([
            r.date,
            r.odometer,
            r.volume,
            r.total_cost,
            r.unit_price or "",
            "是" if r.full_tank else "否",
            r.gas_station or "",
            f"{r.fuel_consumption:.1f}" if r.fuel_consumption else "",
            r.notes or ""
        ])

    # 调整列宽
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 10
    ws.column_dimensions['F'].width = 10
    ws.column_dimensions['G'].width = 15
    ws.column_dimensions['H'].width = 12
    ws.column_dimensions['I'].width = 20

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"fuel_records_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
