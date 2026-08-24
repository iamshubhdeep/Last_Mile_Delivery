import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "app/routers/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.models.user import User
from app.models.agent import AgentProfile
from app.schemas.auth import UserCreate, UserOut, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.utils.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pwd,
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    if new_user.role == "AGENT":
        agent_prof = AgentProfile(user_id=new_user.id)
        db.add(agent_prof)
        db.commit()
        
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
""",

    "app/routers/zones.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.zone import Zone, ZoneArea
from app.schemas.zone import ZoneCreate, ZoneOut, ZoneAreaCreate, ZoneAreaOut
from app.utils.deps import get_current_admin

router = APIRouter(prefix="/api/zones", tags=["Zones"])

@router.post("/", response_model=ZoneOut)
def create_zone(zone_data: ZoneCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    new_zone = Zone(**zone_data.model_dump())
    db.add(new_zone)
    db.commit()
    db.refresh(new_zone)
    return new_zone

@router.get("/", response_model=List[ZoneOut])
def list_zones(db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return db.query(Zone).all()

@router.post("/{zone_id}/areas", response_model=ZoneAreaOut)
def add_area(zone_id: int, area_data: ZoneAreaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    new_area = ZoneArea(zone_id=zone_id, **area_data.model_dump())
    db.add(new_area)
    db.commit()
    db.refresh(new_area)
    return new_area

@router.get("/{zone_id}/areas", response_model=List[ZoneAreaOut])
def list_areas(zone_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return db.query(ZoneArea).filter(ZoneArea.zone_id == zone_id).all()

@router.get("/detect")
def detect_zone(pincode: str, db: Session = Depends(get_db)):
    area = db.query(ZoneArea).filter(ZoneArea.pincode == pincode).first()
    if not area:
        raise HTTPException(status_code=404, detail="Zone not found for this pincode")
    return {"zone_id": area.zone_id, "pincode": area.pincode, "area_name": area.area_name}
""",

    "app/routers/rate_cards.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.rate_card import RateCard, CODSurcharge
from app.schemas.rate_card import RateCardCreate, RateCardOut, CODSurchargeCreate, CODSurchargeOut
from app.utils.deps import get_current_admin

router = APIRouter(prefix="/api/rate-cards", tags=["Rate Cards"])

@router.post("/", response_model=RateCardOut)
def create_rate_card(data: RateCardCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    rc = db.query(RateCard).filter(
        RateCard.source_zone_id == data.source_zone_id,
        RateCard.dest_zone_id == data.dest_zone_id,
        RateCard.order_type == data.order_type
    ).first()
    if rc:
        rc.rate_per_kg = data.rate_per_kg
        rc.min_charge = data.min_charge
    else:
        rc = RateCard(**data.model_dump())
        db.add(rc)
    db.commit()
    db.refresh(rc)
    return rc

@router.get("/", response_model=List[RateCardOut])
def list_rate_cards(db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return db.query(RateCard).all()

router_cod = APIRouter(prefix="/api/cod-surcharges", tags=["COD Surcharges"])

@router_cod.post("/", response_model=CODSurchargeOut)
def set_cod_surcharge(data: CODSurchargeCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    cod = db.query(CODSurcharge).filter(CODSurcharge.order_type == data.order_type).first()
    if cod:
        cod.surcharge_amount = data.surcharge_amount
    else:
        cod = CODSurcharge(**data.model_dump())
        db.add(cod)
    db.commit()
    db.refresh(cod)
    return cod

@router_cod.get("/", response_model=List[CODSurchargeOut])
def list_cod_surcharges(db: Session = Depends(get_db), current_user = Depends(get_current_admin)):
    return db.query(CODSurcharge).all()
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 5 generated successfully.")
