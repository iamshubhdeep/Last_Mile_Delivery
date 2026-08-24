from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from datetime import datetime
import uuid
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    pickup_address = Column(String, nullable=False)
    pickup_pincode = Column(String, nullable=False)
    drop_address = Column(String, nullable=False)
    drop_pincode = Column(String, nullable=False)
    pickup_zone_id = Column(Integer, ForeignKey("zones.id"))
    drop_zone_id = Column(Integer, ForeignKey("zones.id"))
    length = Column(Numeric(10, 2), nullable=False)
    breadth = Column(Numeric(10, 2), nullable=False)
    height = Column(Numeric(10, 2), nullable=False)
    actual_weight = Column(Numeric(10, 2), nullable=False)
    volumetric_weight = Column(Numeric(10, 2), nullable=False)
    billable_weight = Column(Numeric(10, 2), nullable=False)
    order_type = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    base_charge = Column(Numeric(10, 2), nullable=False)
    cod_surcharge = Column(Numeric(10, 2), default=0, nullable=False)
    total_charge = Column(Numeric(10, 2), nullable=False)
    current_status = Column(String, nullable=False, default="Created")
    scheduled_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class OrderTracking(Base):
    __tablename__ = "order_tracking"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    status = Column(String, nullable=False)
    changed_by_id = Column(String(36), ForeignKey("users.id"))
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
