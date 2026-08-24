from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    areas = relationship("ZoneArea", back_populates="zone")

class ZoneArea(Base):
    __tablename__ = "zone_areas"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    pincode = Column(String, index=True, nullable=False)
    area_name = Column(String)
    zone = relationship("Zone", back_populates="areas")
