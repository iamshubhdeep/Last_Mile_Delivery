import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "app/schemas/order.py": """from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
import uuid
from datetime import datetime

class OrderCalculate(BaseModel):
    pickup_pincode: str
    drop_pincode: str
    length: Decimal
    breadth: Decimal
    height: Decimal
    actual_weight: Decimal
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
    customer_id: Optional[uuid.UUID] = None  # Admin can pass this

class OrderStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class OrderTrackingOut(BaseModel):
    id: int
    status: str
    changed_by_id: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    agent_id: Optional[uuid.UUID]
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
""",

    "app/schemas/agent.py": """from pydantic import BaseModel
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
    user_id: uuid.UUID
    current_zone_id: Optional[int]
    is_available: bool
    latitude: Optional[float]
    longitude: Optional[float]
    class Config:
        from_attributes = True
""",

    "app/utils/auth.py": """from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
""",

    "app/utils/deps.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def get_current_agent(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["AGENT", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 3 generated successfully.")
