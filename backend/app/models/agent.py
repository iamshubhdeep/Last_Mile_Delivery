from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, String
from app.database import Base

class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    current_zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
