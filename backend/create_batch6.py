import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Shubhdeep\OneDrive\Desktop\LastMile\backend")

files_content = {
    "app/routers/orders.py": """from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.order import Order, OrderTracking
from app.models.user import User
from app.models.agent import AgentProfile
from app.schemas.order import OrderCalculate, OrderCalculateResult, OrderCreate, OrderOut, OrderStatusUpdate, OrderTrackingOut
from app.utils.deps import get_current_user, get_current_admin, get_current_agent
from app.services.rate_calculator import calculate_charge
from app.services.assignment import auto_assign_agent
from app.services.notifications import send_notification

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def log_tracking(db: Session, order_id: uuid.UUID, status: str, user_id: uuid.UUID, notes: str = None):
    tracking = OrderTracking(order_id=order_id, status=status, changed_by_id=user_id, notes=notes)
    db.add(tracking)

@router.post("/calculate", response_model=OrderCalculateResult)
def calculate_order_charge(data: OrderCalculate, db: Session = Depends(get_db)):
    return calculate_charge(db, data.pickup_pincode, data.drop_pincode, data.length, data.breadth, data.height, data.actual_weight, data.order_type, data.payment_type)

@router.post("/", response_model=OrderOut)
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    calc = calculate_charge(db, data.pickup_pincode, data.drop_pincode, data.length, data.breadth, data.height, data.actual_weight, data.order_type, data.payment_type)
    
    customer_id = current_user.id
    if current_user.role == "ADMIN" and data.customer_id:
        customer_id = data.customer_id
        
    order = Order(
        customer_id=customer_id,
        pickup_address=data.pickup_address,
        pickup_pincode=data.pickup_pincode,
        drop_address=data.drop_address,
        drop_pincode=data.drop_pincode,
        pickup_zone_id=calc["pickup_zone_id"],
        drop_zone_id=calc["drop_zone_id"],
        length=data.length,
        breadth=data.breadth,
        height=data.height,
        actual_weight=data.actual_weight,
        volumetric_weight=calc["volumetric_weight"],
        billable_weight=calc["billable_weight"],
        order_type=data.order_type,
        payment_type=data.payment_type,
        base_charge=calc["base_charge"],
        cod_surcharge=calc["cod_surcharge"],
        total_charge=calc["total_charge"],
        scheduled_date=data.scheduled_date
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    log_tracking(db, order.id, "Created", current_user.id)
    db.commit()
    
    cust = db.query(User).filter(User.id == customer_id).first()
    if cust:
        send_notification(cust.email, "Order Created", f"Your order {order.id} has been created.")
        
    return order

@router.get("/", response_model=List[OrderOut])
def list_orders(status: Optional[str] = None, zone_id: Optional[int] = None, agent_id: Optional[uuid.UUID] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Order)
    if current_user.role == "CUSTOMER":
        query = query.filter(Order.customer_id == current_user.id)
    elif current_user.role == "AGENT":
        query = query.filter(Order.agent_id == current_user.id)
    else: # ADMIN
        if status:
            query = query.filter(Order.current_status == status)
        if zone_id:
            query = query.filter((Order.pickup_zone_id == zone_id) | (Order.drop_zone_id == zone_id))
        if agent_id:
            query = query.filter(Order.agent_id == agent_id)
            
    return query.all()

@router.get("/{order_id}")
def get_order(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.role == "CUSTOMER" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    tracking = db.query(OrderTracking).filter(OrderTracking.order_id == order.id).order_by(OrderTracking.created_at.asc()).all()
    
    return {"order": order, "tracking": tracking}

@router.put("/{order_id}/assign")
def assign_agent_manual(order_id: uuid.UUID, agent_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    agent = db.query(User).filter(User.id == agent_id, User.role == "AGENT").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    order.agent_id = agent_id
    order.current_status = "Assigned"
    db.commit()
    
    log_tracking(db, order.id, "Assigned", current_user.id, f"Manually assigned to {agent.name}")
    db.commit()
    
    send_notification(agent.email, "New Order Assigned", f"Order {order.id} has been assigned to you.")
    
    return {"status": "success", "agent_id": agent_id}

@router.post("/{order_id}/auto-assign")
def assign_agent_auto(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    assigned_agent_id = auto_assign_agent(db, order)
    if not assigned_agent_id:
        raise HTTPException(status_code=400, detail="No available agents")
        
    order.agent_id = assigned_agent_id
    order.current_status = "Assigned"
    
    # Mark agent as unavailable
    agent_prof = db.query(AgentProfile).filter(AgentProfile.user_id == assigned_agent_id).first()
    if agent_prof:
        agent_prof.is_available = False
        
    db.commit()
    
    log_tracking(db, order.id, "Assigned", current_user.id, "Auto-assigned")
    db.commit()
    
    agent = db.query(User).filter(User.id == assigned_agent_id).first()
    send_notification(agent.email, "New Order Assigned", f"Order {order.id} has been auto-assigned to you.")
    
    return {"status": "success", "agent_id": assigned_agent_id}

@router.put("/{order_id}/status")
def update_status(order_id: uuid.UUID, data: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if current_user.role == "AGENT" and order.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized for this order")
        
    valid_statuses = ["Picked Up", "In Transit", "Out for Delivery", "Delivered", "Failed"]
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status update")
        
    order.current_status = data.status
    db.commit()
    
    log_tracking(db, order.id, data.status, current_user.id, data.notes)
    db.commit()
    
    cust = db.query(User).filter(User.id == order.customer_id).first()
    send_notification(cust.email, "Order Status Update", f"Your order {order.id} is now {data.status}")
    
    return order

@router.put("/{order_id}/override-status")
def override_status(order_id: uuid.UUID, data: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.current_status = data.status
    db.commit()
    
    log_tracking(db, order.id, data.status, current_user.id, f"OVERRIDE: {data.notes}")
    db.commit()
    return order

@router.post("/{order_id}/reschedule")
def reschedule_order(order_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if current_user.role == "CUSTOMER" and order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if order.current_status != "Failed":
        raise HTTPException(status_code=400, detail="Only failed orders can be rescheduled")
        
    order.current_status = "Assigned"
    db.commit()
    
    log_tracking(db, order.id, "Rescheduled", current_user.id, "Customer requested reschedule")
    db.commit()
    return order
""",

    "app/routers/agents.py": """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.agent import AgentProfile
from app.models.order import Order
from app.schemas.agent import AgentProfileOut, AgentLocationUpdate, AgentAvailabilityUpdate
from app.schemas.order import OrderOut
from app.utils.deps import get_current_user, get_current_admin, get_current_agent

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("/", response_model=List[AgentProfileOut])
def list_agents(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    return db.query(AgentProfile).all()

@router.put("/location")
def update_location(data: AgentLocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    prof = db.query(AgentProfile).filter(AgentProfile.user_id == current_user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Agent profile not found")
        
    prof.latitude = data.latitude
    prof.longitude = data.longitude
    if data.current_zone_id:
        prof.current_zone_id = data.current_zone_id
    db.commit()
    return {"status": "updated"}

@router.put("/availability")
def update_availability(data: AgentAvailabilityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    prof = db.query(AgentProfile).filter(AgentProfile.user_id == current_user.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Agent profile not found")
        
    prof.is_available = data.is_available
    db.commit()
    return {"status": "updated", "is_available": prof.is_available}

@router.get("/orders", response_model=List[OrderOut])
def view_assigned_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_agent)):
    return db.query(Order).filter(Order.agent_id == current_user.id).all()
""",

    "app/main.py": """from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, zones, rate_cards, orders, agents

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Last-Mile Delivery Tracker")

app.include_router(auth.router)
app.include_router(zones.router)
app.include_router(rate_cards.router)
app.include_router(rate_cards.router_cod)
app.include_router(orders.router)
app.include_router(agents.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Last-Mile Delivery Tracker API"}
""",

    "seed.py": """from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.zone import Zone, ZoneArea
from app.models.rate_card import RateCard, CODSurcharge
from app.models.agent import AgentProfile
from app.utils.auth import get_password_hash
from decimal import Decimal

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if seeded
    if db.query(User).filter(User.email == "admin@test.com").first():
        print("Already seeded.")
        return
        
    # Users
    admin = User(email="admin@test.com", password_hash=get_password_hash("password"), name="Admin", phone="123", role="ADMIN")
    agent = User(email="agent@test.com", password_hash=get_password_hash("password"), name="Agent One", phone="456", role="AGENT")
    customer = User(email="customer@test.com", password_hash=get_password_hash("password"), name="Customer", phone="789", role="CUSTOMER")
    
    db.add_all([admin, agent, customer])
    db.commit()
    
    # Agent Profile
    db.add(AgentProfile(user_id=agent.id, is_available=True))
    db.commit()
    
    # Zones
    z1 = Zone(name="North Zone")
    z2 = Zone(name="South Zone")
    db.add_all([z1, z2])
    db.commit()
    
    db.add_all([
        ZoneArea(zone_id=z1.id, pincode="110001", area_name="Connaught Place"),
        ZoneArea(zone_id=z2.id, pincode="600001", area_name="Chennai Central")
    ])
    db.commit()
    
    # Rate Cards
    rc = RateCard(source_zone_id=z1.id, dest_zone_id=z2.id, order_type="B2C", rate_per_kg=Decimal("50.00"), min_charge=Decimal("100.00"))
    db.add(rc)
    
    # COD Surcharge
    cod = CODSurcharge(order_type="B2C", surcharge_amount=Decimal("30.00"))
    db.add(cod)
    
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed()
"""
}

for filepath, content in files_content.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Batch 6 generated successfully.")
