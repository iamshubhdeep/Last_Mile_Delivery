from decimal import Decimal
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.zone import Zone, ZoneArea
from app.models.rate_card import RateCard, CODSurcharge
from app.models.agent import AgentProfile
from app.utils.auth import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@test.com").first():
            print("Already seeded.")
            return

        admin = User(email="admin@test.com", password_hash=get_password_hash("password"), name="Admin", phone="123", role="ADMIN")
        agent = User(email="agent@test.com", password_hash=get_password_hash("password"), name="Agent One", phone="456", role="AGENT")
        agent2 = User(email="agent2@test.com", password_hash=get_password_hash("password"), name="Agent Two", phone="457", role="AGENT")
        customer = User(email="customer@test.com", password_hash=get_password_hash("password"), name="Customer", phone="789", role="CUSTOMER")
        db.add_all([admin, agent, agent2, customer])
        db.commit()

        z1 = Zone(name="North Zone", description="North service area")
        z2 = Zone(name="South Zone", description="South service area")
        db.add_all([z1, z2])
        db.commit()
        db.add_all([
            ZoneArea(zone_id=z1.id, pincode="110001", area_name="Connaught Place"),
            ZoneArea(zone_id=z1.id, pincode="110002", area_name="New Delhi"),
            ZoneArea(zone_id=z2.id, pincode="600001", area_name="Chennai Central"),
            ZoneArea(zone_id=z2.id, pincode="600002", area_name="Chennai North"),
        ])
        db.add_all([
            AgentProfile(user_id=agent.id, current_zone_id=z1.id, is_available=True, latitude=28.6315, longitude=77.2167),
            AgentProfile(user_id=agent2.id, current_zone_id=z2.id, is_available=True, latitude=13.0827, longitude=80.2707),
        ])

        # Intra-zone and inter-zone rates for both B2B and B2C.
        for source, dest, values in [
            (z1.id, z1.id, [("B2B", "40", "80"), ("B2C", "50", "100")]),
            (z2.id, z2.id, [("B2B", "40", "80"), ("B2C", "50", "100")]),
            (z1.id, z2.id, [("B2B", "60", "120"), ("B2C", "70", "140")]),
            (z2.id, z1.id, [("B2B", "60", "120"), ("B2C", "70", "140")]),
        ]:
            for order_type, rate, minimum in values:
                db.add(RateCard(source_zone_id=source, dest_zone_id=dest, order_type=order_type,
                                rate_per_kg=Decimal(rate), min_charge=Decimal(minimum)))
        db.add_all([
            CODSurcharge(order_type="B2B", surcharge_amount=Decimal("25")),
            CODSurcharge(order_type="B2C", surcharge_amount=Decimal("30")),
        ])
        db.commit()
        print("Seeding complete.")
        print("Admin: admin@test.com / password")
        print("Agent: agent@test.com / password")
        print("Agent 2: agent2@test.com / password")
        print("Customer: customer@test.com / password")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
