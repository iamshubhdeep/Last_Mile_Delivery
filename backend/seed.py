from app.database import SessionLocal, engine, Base
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
