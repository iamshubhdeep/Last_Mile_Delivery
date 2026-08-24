from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class RateCardCreate(BaseModel):
    source_zone_id: int
    dest_zone_id: int
    order_type: str
    rate_per_kg: Decimal
    min_charge: Decimal

class RateCardOut(RateCardCreate):
    id: int
    class Config:
        from_attributes = True

class CODSurchargeCreate(BaseModel):
    order_type: str
    surcharge_amount: Decimal

class CODSurchargeOut(CODSurchargeCreate):
    id: int
    class Config:
        from_attributes = True
