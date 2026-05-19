from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional

class RecordCreate(BaseModel):
    vehicle_id: int = Field(..., description="车辆ID")
    date: str = Field(..., description="日期 YYYY-MM-DD")
    odometer: int = Field(..., description="当前里程")
    volume: Optional[float] = Field(None, gt=0, description="加油量(升)")
    total_cost: float = Field(..., gt=0, description="总金额")
    unit_price: Optional[float] = Field(None, ge=0, description="单价(元/升)")

    @model_validator(mode='after')
    def derive_volume_or_price(self):
        if self.volume is None and (self.unit_price is None or self.unit_price <= 0):
            raise ValueError('volume 和 unit_price 至少需要提供一个')
        if self.volume is None and self.unit_price and self.unit_price > 0:
            self.volume = round(self.total_cost / self.unit_price, 2)
        return self
    full_tank: bool = Field(True, description="是否加满")
    gas_station: Optional[str] = Field(None, description="加油站")
    notes: Optional[str] = Field(None, description="备注")

class RecordUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    date: Optional[str] = None
    odometer: Optional[int] = None
    volume: Optional[float] = Field(None, gt=0)
    total_cost: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    full_tank: Optional[bool] = None
    gas_station: Optional[str] = None
    notes: Optional[str] = None

class RecordResponse(BaseModel):
    id: int
    vehicle_id: int
    date: str
    odometer: int
    volume: float
    total_cost: float
    unit_price: Optional[float]
    full_tank: bool
    gas_station: Optional[str]
    notes: Optional[str]
    fuel_consumption: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}

class RecordListParams(BaseModel):
    vehicle_id: Optional[int] = None
    page: int = 1
    page_size: int = 20
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    total: int
    page: int
    page_size: int
