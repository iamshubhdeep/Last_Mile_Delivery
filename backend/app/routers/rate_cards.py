from fastapi import APIRouter, Depends, HTTPException
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
