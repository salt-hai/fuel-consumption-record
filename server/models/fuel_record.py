from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class FuelRecord(Base):
    __tablename__ = "fuel_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    odometer = Column(Integer, nullable=False)
    volume = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    unit_price = Column(Float)
    full_tank = Column(Boolean, default=True)
    gas_station = Column(String)
    notes = Column(String)
    fuel_consumption = Column(Float)  # L/100km, computed
    created_at = Column(DateTime, server_default=func.current_timestamp())

    vehicle = relationship("Vehicle", back_populates="fuel_records")
