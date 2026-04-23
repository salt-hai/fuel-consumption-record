from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MaintenanceCreate(BaseModel):
    vehicle_id: int = Field(..., description="车辆ID")
    type: str = Field(..., description="保养类型")
    date: str = Field(..., description="日期 YYYY-MM-DD")
    odometer: int = Field(..., description="当前里程")
    cost: Optional[float] = Field(None, description="费用")
    description: Optional[str] = Field(None, description="描述")
    next_maintenance_odometer: Optional[int] = Field(None, description="下次保养里程")
    next_maintenance_date: Optional[str] = Field(None, description="下次保养日期")

class MaintenanceUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    type: Optional[str] = None
    date: Optional[str] = None
    odometer: Optional[int] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    next_maintenance_odometer: Optional[int] = None
    next_maintenance_date: Optional[str] = None
    is_completed: Optional[bool] = None

class MaintenanceResponse(BaseModel):
    id: int
    vehicle_id: int
    type: str
    date: str
    odometer: int
    cost: Optional[float]
    description: Optional[str]
    next_maintenance_odometer: Optional[int]
    next_maintenance_date: Optional[str]
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
