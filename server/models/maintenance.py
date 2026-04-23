from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, func
from database import Base

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    type = Column(String, nullable=False)  # 保养类型
    date = Column(String, nullable=False)
    odometer = Column(Integer, nullable=False)
    cost = Column(Float)
    description = Column(String)
    next_maintenance_odometer = Column(Integer)
    next_maintenance_date = Column(String)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
