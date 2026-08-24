import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "app/services/rate_calculator.py": """from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.zone import ZoneArea
from app.models.rate_card import RateCard, CODSurcharge
from fastapi import HTTPException

def get_zone_by_pincode(db: Session, pincode: str):
    area = db.query(ZoneArea).filter(ZoneArea.pincode == pincode).first()
    return area.zone_id if area else None

def calculate_charge(db: Session, pickup_pincode: str, drop_pincode: str,
                     length: Decimal, breadth: Decimal, height: Decimal, actual_weight: Decimal,
                     order_type: str, payment_type: str):
                     
    pickup_zone_id = get_zone_by_pincode(db, pickup_pincode)
    drop_zone_id = get_zone_by_pincode(db, drop_pincode)
    
    if not pickup_zone_id or not drop_zone_id:
        raise HTTPException(status_code=400, detail="Service not available for given pincodes")
        
    volumetric_weight = (length * breadth * height) / Decimal(5000.0)
    billable_weight = max(actual_weight, volumetric_weight)
    
    rate_card = db.query(RateCard).filter(
        RateCard.source_zone_id == pickup_zone_id,
        RateCard.dest_zone_id == drop_zone_id,
        RateCard.order_type == order_type
    ).first()
    
    if not rate_card:
        raise HTTPException(status_code=400, detail="No rate card found for this route and order type")
        
    base_charge = max(billable_weight * rate_card.rate_per_kg, rate_card.min_charge)
    
    cod_surcharge_amount = Decimal(0)
    if payment_type == "COD":
        cod_rule = db.query(CODSurcharge).filter(CODSurcharge.order_type == order_type).first()
        if cod_rule:
            cod_surcharge_amount = cod_rule.surcharge_amount
            
    total_charge = base_charge + cod_surcharge_amount
    
    return {
        "volumetric_weight": volumetric_weight,
        "billable_weight": billable_weight,
        "base_charge": base_charge,
        "cod_surcharge": cod_surcharge_amount,
        "total_charge": total_charge,
        "pickup_zone_id": pickup_zone_id,
        "drop_zone_id": drop_zone_id
    }
""",

    "app/services/assignment.py": """import math
from sqlalchemy.orm import Session
from app.models.agent import AgentProfile

def calculate_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def auto_assign_agent(db: Session, order):
    # Prefer agents in same zone
    agents = db.query(AgentProfile).filter(
        AgentProfile.is_available == True,
        AgentProfile.current_zone_id == order.pickup_zone_id
    ).all()
    
    if not agents:
        # Fallback to any available agent
        agents = db.query(AgentProfile).filter(AgentProfile.is_available == True).all()
        
    if not agents:
        return None
        
    # Pick randomly or by distance (simulated as random here if no lat/lng)
    # If order had lat/lng we could do nearest neighbor. For now pick first.
    best_agent = agents[0]
    
    return best_agent.user_id
""",

    "app/services/notifications.py": """import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from app.config import settings

def send_email_sync(to_email: str, subject: str, body: str):
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP credentials not set. Skipping email.")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def send_notification(to_email: str, subject: str, body: str):
    thread = threading.Thread(target=send_email_sync, args=(to_email, subject, body))
    thread.start()
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 4 generated successfully.")
