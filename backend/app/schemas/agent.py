from pydantic import BaseModel
from typing import Optional
import uuid

class AgentLocationUpdate(BaseModel):
    latitude: float
    longitude: float
    current_zone_id: Optional[int] = None

class AgentAvailabilityUpdate(BaseModel):
    is_available: bool

class AgentProfileOut(BaseModel):
    id: int
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    current_zone_id: Optional[int]
    is_available: bool
    latitude: Optional[float]
    longitude: Optional[float]
    class Config:
        from_attributes = True
