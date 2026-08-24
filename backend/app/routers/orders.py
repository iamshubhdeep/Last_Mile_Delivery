from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.order import Order, OrderTracking
from app.models.user import User
from app.models.agent import AgentProfile
from app.schemas.order import OrderCalculate, OrderCalculateResult, OrderCreate, OrderOut, OrderStatusUpdate, RescheduleRequest
from app.utils.deps import get_current_user, get_current_admin
from app.services.rate_calculator import calculate_charge
from app.services.assignment import auto_assign_agent
from app.services.notifications import send_notification

router = APIRouter(prefix="/api/orders", tags=["Orders"])

STATUS_FLOW = ["Created", "Assigned", "Picked Up", "In Transit", "Out for Delivery", "Delivered", "Failed"]
AGENT_STATUSES = STATUS_FLOW[2:]

def log_tracking(db, order_id, status, user_id, notes=None):
    db.add(OrderTracking(order_id=order_id, status=status, changed_by_id=user_id, notes=notes))

@router.post("/calculate", response_model=OrderCalculateResult)
def calculate_order_charge(data: OrderCalculate, db: Session = Depends(get_db)):
    return calculate_charge(db, **data.model_dump())

@router.post("/", response_model=OrderOut)
def create_order(data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    customer_id = current_user.id
    if current_user.role == "ADMIN":
        if not data.customer_id:
            raise HTTPException(status_code=400, detail="Admin must provide customer_id")
        customer = db.query(User).filter(User.id == data.customer_id, User.role == "CUSTOMER").first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer_id = customer.id
    elif data.customer_id and data.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create an order for another customer")

    calc = calculate_charge(db, **data.model_dump(exclude={"pickup_address", "drop_address", "scheduled_date", "customer_id"}))
    order = Order(customer_id=customer_id, pickup_address=data.pickup_address, pickup_pincode=data.pickup_pincode,
                  drop_address=data.drop_address, drop_pincode=data.drop_pincode,
                  pickup_zone_id=calc["pickup_zone_id"], drop_zone_id=calc["drop_zone_id"],
                  length=data.length, breadth=data.breadth, height=data.height, actual_weight=data.actual_weight,
                  volumetric_weight=calc["volumetric_weight"], billable_weight=calc["billable_weight"],
                  order_type=data.order_type.upper(), payment_type=data.payment_type.upper(),
                  base_charge=calc["base_charge"], cod_surcharge=calc["cod_surcharge"], total_charge=calc["total_charge"],
                  scheduled_date=data.scheduled_date)
    db.add(order)
    db.flush()
    log_tracking(db, order.id, "Created", current_user.id)
    db.commit()
    db.refresh(order)
    send_notification(db.query(User).filter(User.id == customer_id).first().email, "Order Created", f"Your order {order.id} has been created.")
    return order

@router.get("/", response_model=List[OrderOut])
def list_orders(status: Optional[str] = None, zone_id: Optional[int] = None, agent_id: Optional[str] = None,
                db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Order)
    if current_user.role == "CUSTOMER":
        query = query.filter(Order.customer_id == current_user.id)
    elif current_user.role == "AGENT":
        query = query.filter(Order.agent_id == current_user.id)
    else:
        if status: query = query.filter(Order.current_status == status)
        if zone_id: query = query.filter((Order.pickup_zone_id == zone_id) | (Order.drop_zone_id == zone_id))
        if agent_id: query = query.filter(Order.agent_id == agent_id)
    return query.order_by(Order.created_at.desc()).all()

@router.get("/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == "CUSTOMER" and order.customer_id != current_user.id: raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == "AGENT" and order.agent_id != current_user.id: raise HTTPException(status_code=403, detail="Not authorized")
    tracking = db.query(OrderTracking).filter(OrderTracking.order_id == order.id).order_by(OrderTracking.created_at.asc(), OrderTracking.id.asc()).all()
    return {"order": order, "tracking": tracking}

@router.put("/{order_id}/assign")
def assign_agent_manual(order_id: str, agent_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    agent = db.query(User).filter(User.id == agent_id, User.role == "AGENT", User.is_active.is_(True)).first()
    profile = db.query(AgentProfile).filter(AgentProfile.user_id == agent_id).first() if agent else None
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if not agent or not profile: raise HTTPException(status_code=404, detail="Agent not found")
    if order.agent_id and order.agent_id != agent_id:
        old = db.query(AgentProfile).filter(AgentProfile.user_id == order.agent_id).first()
        if old: old.is_available = True
    order.agent_id = agent_id
    order.current_status = "Assigned"
    profile.is_available = False
    log_tracking(db, order.id, "Assigned", current_user.id, f"Manually assigned to {agent.name}")
    db.commit()
    send_notification(agent.email, "New Order Assigned", f"Order {order.id} has been assigned to you.")
    return {"status": "success", "agent_id": agent_id}

@router.post("/{order_id}/auto-assign")
def assign_agent_auto(order_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    assigned_agent_id = auto_assign_agent(db, order)
    if not assigned_agent_id: raise HTTPException(status_code=400, detail="No available agents")
    agent_prof = db.query(AgentProfile).filter(AgentProfile.user_id == assigned_agent_id).first()
    agent = db.query(User).filter(User.id == assigned_agent_id).first()
    order.agent_id = assigned_agent_id
    order.current_status = "Assigned"
    agent_prof.is_available = False
    log_tracking(db, order.id, "Assigned", current_user.id, "Auto-assigned to nearest available agent")
    db.commit()
    send_notification(agent.email, "New Order Assigned", f"Order {order.id} has been auto-assigned to you.")
    return {"status": "success", "agent_id": assigned_agent_id}

@router.put("/{order_id}/status")
def update_status(order_id: str, data: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != "AGENT" or order.agent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the assigned agent can update delivery status")
    if data.status not in AGENT_STATUSES: raise HTTPException(status_code=400, detail="Invalid status update")
    order.current_status = data.status
    if data.status in ("Delivered", "Failed"):
        profile = db.query(AgentProfile).filter(AgentProfile.user_id == current_user.id).first()
        if profile: profile.is_available = True
    log_tracking(db, order.id, data.status, current_user.id, data.notes)
    db.commit()
    cust = db.query(User).filter(User.id == order.customer_id).first()
    if cust: send_notification(cust.email, "Order Status Update", f"Your order {order.id} is now {data.status}")
    return order

@router.put("/{order_id}/override-status", response_model=OrderOut)
def override_status(order_id: str, data: OrderStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    order.current_status = data.status
    log_tracking(db, order.id, data.status, current_user.id, f"OVERRIDE: {data.notes or ''}")
    db.commit()
    return order

@router.post("/{order_id}/reschedule", response_model=OrderOut)
def reschedule_order(order_id: str, data: RescheduleRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order: raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == "CUSTOMER" and order.customer_id != current_user.id: raise HTTPException(status_code=403, detail="Not authorized")
    if order.current_status != "Failed": raise HTTPException(status_code=400, detail="Only failed orders can be rescheduled")
    old_agent_id = order.agent_id
    if old_agent_id:
        old_profile = db.query(AgentProfile).filter(AgentProfile.user_id == old_agent_id).first()
        if old_profile: old_profile.is_available = True
    order.agent_id = None
    order.scheduled_date = data.scheduled_date
    order.current_status = "Created"
    log_tracking(db, order.id, "Rescheduled", current_user.id, f"Rescheduled for {data.scheduled_date.isoformat()}")
    db.flush()

    # Reassign a new available agent for the rescheduled attempt.
    new_agent_id = auto_assign_agent(db, order, exclude_user_id=old_agent_id)
    if new_agent_id:
        new_profile = db.query(AgentProfile).filter(AgentProfile.user_id == new_agent_id).first()
        new_agent = db.query(User).filter(User.id == new_agent_id).first()
        order.agent_id = new_agent_id
        order.current_status = "Assigned"
        if new_profile:
            new_profile.is_available = False
        log_tracking(db, order.id, "Assigned", current_user.id, "Reassigned after failed delivery")
        if new_agent:
            send_notification(new_agent.email, "Rescheduled Order Assigned", f"Order {order.id} has been reassigned for the new delivery attempt.")
    db.commit()
    return order
