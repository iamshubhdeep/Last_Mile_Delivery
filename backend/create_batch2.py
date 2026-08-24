import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "app/models/order.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    pickup_address = Column(String, nullable=False)
    pickup_pincode = Column(String, nullable=False)
    drop_address = Column(String, nullable=False)
    drop_pincode = Column(String, nullable=False)
    pickup_zone_id = Column(Integer, ForeignKey("zones.id"))
    drop_zone_id = Column(Integer, ForeignKey("zones.id"))
    length = Column(Numeric(10, 2))
    breadth = Column(Numeric(10, 2))
    height = Column(Numeric(10, 2))
    actual_weight = Column(Numeric(10, 2))
    volumetric_weight = Column(Numeric(10, 2))
    billable_weight = Column(Numeric(10, 2))
    order_type = Column(String, nullable=False) # B2B, B2C
    payment_type = Column(String, nullable=False) # PREPAID, COD
    base_charge = Column(Numeric(10, 2))
    cod_surcharge = Column(Numeric(10, 2), default=0)
    total_charge = Column(Numeric(10, 2))
    current_status = Column(String, nullable=False, default="Created")
    scheduled_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderTracking(Base):
    __tablename__ = "order_tracking"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    status = Column(String, nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
""",

    "app/models/agent.py": """from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    current_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    is_available = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
""",

    "app/schemas/auth.py": """from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    role: Optional[str] = "CUSTOMER"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True
""",

    "app/schemas/zone.py": """from pydantic import BaseModel
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
""",

    "app/schemas/rate_card.py": """from pydantic import BaseModel
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
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 2 generated successfully.")
