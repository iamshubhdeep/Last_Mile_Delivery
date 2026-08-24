from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from datetime import datetime
from app.database import Base

class RateCard(Base):
    __tablename__ = "rate_cards"
    id = Column(Integer, primary_key=True, index=True)
    source_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    dest_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    order_type = Column(String, nullable=False) # B2B, B2C
    rate_per_kg = Column(Numeric(10, 2), nullable=False)
    min_charge = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class CODSurcharge(Base):
    __tablename__ = "cod_surcharges"
    id = Column(Integer, primary_key=True, index=True)
    order_type = Column(String, unique=True, nullable=False)
    surcharge_amount = Column(Numeric(10, 2), nullable=False)
