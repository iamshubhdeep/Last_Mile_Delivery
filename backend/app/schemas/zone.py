from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None

class ZoneCreate(ZoneBase):
    pass

class ZoneOut(ZoneBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ZoneAreaCreate(BaseModel):
    pincode: str
    area_name: Optional[str] = None

class ZoneAreaOut(ZoneAreaCreate):
    id: int
    zone_id: int
    class Config:
        from_attributes = True
