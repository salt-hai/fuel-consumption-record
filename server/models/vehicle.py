from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    icon = Column(String, default="🚗")
    brand = Column(String)
    model = Column(String)
    plate_number = Column(String, unique=True)
    initial_odometer = Column(Integer, default=0)
    fuel_type = Column(String, default="92号汽油")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    fuel_records = relationship("FuelRecord", back_populates="vehicle")
