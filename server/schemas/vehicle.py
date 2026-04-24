from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class VehicleCreate(BaseModel):
    name: str = Field(..., description="车辆名称")
    icon: str = Field("🚗", description="车辆图标")
    brand: Optional[str] = Field(None, description="品牌")
    model: Optional[str] = Field(None, description="型号")
    plate_number: Optional[str] = Field(None, description="车牌号")
    initial_odometer: int = Field(0, description="初始里程")
    fuel_type: str = Field("92号汽油", description="燃油类型")

class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = Field(None, description="车辆图标")
    brand: Optional[str] = None
    model: Optional[str] = None
    plate_number: Optional[str] = None
    initial_odometer: Optional[int] = None
    fuel_type: Optional[str] = None
    is_active: Optional[bool] = None

class VehicleResponse(BaseModel):
    id: int
    name: str
    icon: str
    brand: Optional[str]
    model: Optional[str]
    plate_number: Optional[str]
    initial_odometer: int
    fuel_type: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
