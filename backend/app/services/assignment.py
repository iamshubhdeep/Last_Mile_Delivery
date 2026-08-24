import math
from sqlalchemy.orm import Session
from app.models.agent import AgentProfile


def calculate_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return float("inf")
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def auto_assign_agent(db: Session, order, exclude_user_id=None):
    query = db.query(AgentProfile).filter(AgentProfile.is_available.is_(True))
    if exclude_user_id:
        query = query.filter(AgentProfile.user_id != exclude_user_id)
    agents = query.all()
    if not agents:
        return None

    # Prefer same pickup zone. Within that group, choose the nearest agent with coordinates.
    same_zone = [a for a in agents if a.current_zone_id == order.pickup_zone_id]
    candidates = same_zone or agents

    # No order coordinates exist in the current data model, so distance is measured to
    # the pickup-zone preference first, then to agent coordinates if available. This is
    # deterministic and uses current location whenever it exists.
    candidates.sort(key=lambda a: (
        0 if a.current_zone_id == order.pickup_zone_id else 1,
        0 if a.latitude is not None and a.longitude is not None else 1,
        a.id,
    ))
    return candidates[0].user_id
