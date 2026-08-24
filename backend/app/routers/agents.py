from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.agent import AgentProfile
from app.models.order import Order
from app.schemas.agent import AgentProfileOut, AgentLocationUpdate, AgentAvailabilityUpdate
from app.schemas.order import OrderOut
from app.utils.deps import get_current_admin, get_current_agent

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("/", response_model=List[AgentProfileOut])
def list_agents(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    profiles = db.query(AgentProfile).all()
    result = []
    for p in profiles:
        u = db.query(User).filter(User.id == p.user_id).first()
        result.append({"id": p.id, "user_id": p.user_id, "name": u.name if u else None, "email": u.email if u else None,
                       "current_zone_id": p.current_zone_id, "is_available": p.is_available,
                       "latitude": p.latitude, "longitude": p.longitude})
    return result

@router.put("/location")
def update_location(data: AgentLocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    prof = db.query(AgentProfile).filter(AgentProfile.user_id == current_user.id).first()
    if not prof: raise HTTPException(status_code=404, detail="Agent profile not found")
    prof.latitude = data.latitude
    prof.longitude = data.longitude
    if data.current_zone_id is not None: prof.current_zone_id = data.current_zone_id
    db.commit()
    return {"status": "updated", "latitude": prof.latitude, "longitude": prof.longitude, "current_zone_id": prof.current_zone_id}

@router.put("/availability")
def update_availability(data: AgentAvailabilityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    prof = db.query(AgentProfile).filter(AgentProfile.user_id == current_user.id).first()
    if not prof: raise HTTPException(status_code=404, detail="Agent profile not found")
    prof.is_available = data.is_available
    db.commit()
    return {"status": "updated", "is_available": prof.is_available}

@router.get("/orders", response_model=List[OrderOut])
def view_assigned_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    return db.query(Order).filter(Order.agent_id == current_user.id).order_by(Order.created_at.desc()).all()
