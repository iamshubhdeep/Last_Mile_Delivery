from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, zones, rate_cards, orders, agents

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Last-Mile Delivery Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(zones.router)
app.include_router(rate_cards.router)
app.include_router(rate_cards.router_cod)
app.include_router(orders.router)
app.include_router(agents.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Last-Mile Delivery Tracker API", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}
