from fastapi import APIRouter, Depends, HTTPException
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
