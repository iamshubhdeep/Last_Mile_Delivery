from decimal import Decimal, ROUND_UP
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.zone import ZoneArea
from app.models.rate_card import RateCard, CODSurcharge

VALID_ORDER_TYPES = {"B2B", "B2C"}
VALID_PAYMENT_TYPES = {"PREPAID", "COD"}


def get_zone_by_pincode(db: Session, pincode: str):
    area = db.query(ZoneArea).filter(ZoneArea.pincode == pincode).first()
    return area.zone_id if area else None


def calculate_charge(db: Session, pickup_pincode, drop_pincode, length, breadth, height,
                     actual_weight, order_type, payment_type):
    order_type = order_type.upper()
    payment_type = payment_type.upper()
    if order_type not in VALID_ORDER_TYPES:
        raise HTTPException(status_code=400, detail="order_type must be B2B or B2C")
    if payment_type not in VALID_PAYMENT_TYPES:
        raise HTTPException(status_code=400, detail="payment_type must be PREPAID or COD")

    pickup_zone_id = get_zone_by_pincode(db, pickup_pincode)
    drop_zone_id = get_zone_by_pincode(db, drop_pincode)
    if pickup_zone_id is None or drop_zone_id is None:
        raise HTTPException(status_code=400, detail="Service not available for given pincodes")

    volumetric_weight = (Decimal(length) * Decimal(breadth) * Decimal(height)) / Decimal("5000")
    billable_weight = max(Decimal(actual_weight), volumetric_weight)
    # Billable weight is rounded upward to the next 0.5 kg.
    billable_weight = (billable_weight * 2).to_integral_value(rounding=ROUND_UP) / 2

    rate_card = db.query(RateCard).filter(
        RateCard.source_zone_id == pickup_zone_id,
        RateCard.dest_zone_id == drop_zone_id,
        RateCard.order_type == order_type
    ).first()
    if not rate_card:
        raise HTTPException(status_code=400, detail="No rate card found for this route and order type")

    base_charge = max(billable_weight * rate_card.rate_per_kg, rate_card.min_charge)
    cod_surcharge_amount = Decimal("0")
    if payment_type == "COD":
        cod_rule = db.query(CODSurcharge).filter(CODSurcharge.order_type == order_type).first()
        if cod_rule:
            cod_surcharge_amount = cod_rule.surcharge_amount

    return {
        "volumetric_weight": volumetric_weight.quantize(Decimal("0.01")),
        "billable_weight": billable_weight.quantize(Decimal("0.01")),
        "base_charge": base_charge.quantize(Decimal("0.01")),
        "cod_surcharge": cod_surcharge_amount.quantize(Decimal("0.01")),
        "total_charge": (base_charge + cod_surcharge_amount).quantize(Decimal("0.01")),
        "pickup_zone_id": pickup_zone_id,
        "drop_zone_id": drop_zone_id
    }
