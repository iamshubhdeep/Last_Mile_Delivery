import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "requirements.txt": """fastapi==0.103.1
uvicorn==0.23.2
sqlalchemy==2.0.21
psycopg2-binary==2.9.9
pydantic==2.4.2
pydantic-settings==2.0.3
passlib==1.7.4
bcrypt==4.0.1
python-jose==3.3.0
python-multipart==0.0.6
email-validator==2.0.0.post2""",
    
    ".env.example": """DATABASE_URL=postgresql://user:password@localhost:5432/lastmile
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
""",

    "run.py": """import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
""",

    "app/__init__.py": "",
    "app/models/__init__.py": "",
    "app/schemas/__init__.py": "",
    "app/routers/__init__.py": "",
    "app/services/__init__.py": "",
    "app/utils/__init__.py": "",

    "app/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/lastmile"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
""",

    "app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",

    "app/models/user.py": """from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False) # CUSTOMER, AGENT, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
""",

    "app/models/zone.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
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
""",

    "app/models/rate_card.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
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
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 1 generated successfully.")
