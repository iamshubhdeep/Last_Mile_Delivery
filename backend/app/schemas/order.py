from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class OrderCalculate(BaseModel):
    pickup_pincode: str = Field(min_length=4, max_length=10)
    drop_pincode: str = Field(min_length=4, max_length=10)
    length: Decimal = Field(gt=0)
    breadth: Decimal = Field(gt=0)
    height: Decimal = Field(gt=0)
    actual_weight: Decimal = Field(gt=0)
    order_type: str
    payment_type: str

class OrderCalculateResult(BaseModel):
    volumetric_weight: Decimal
    billable_weight: Decimal
    base_charge: Decimal
    cod_surcharge: Decimal
    total_charge: Decimal
    pickup_zone_id: Optional[int]
    drop_zone_id: Optional[int]

class OrderCreate(OrderCalculate):
    pickup_address: str
    drop_address: str
    scheduled_date: Optional[datetime] = None
    customer_id: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class RescheduleRequest(BaseModel):
    scheduled_date: datetime

class OrderTrackingOut(BaseModel):
    id: int
    status: str
    changed_by_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: str
    customer_id: str
    agent_id: Optional[str]
    pickup_address: str
    pickup_pincode: str
    drop_address: str
    drop_pincode: str
    pickup_zone_id: Optional[int]
    drop_zone_id: Optional[int]
    length: Decimal
    breadth: Decimal
    height: Decimal
    actual_weight: Decimal
    volumetric_weight: Decimal
    billable_weight: Decimal
    order_type: str
    payment_type: str
    base_charge: Decimal
    cod_surcharge: Decimal
    total_charge: Decimal
    current_status: str
    scheduled_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
