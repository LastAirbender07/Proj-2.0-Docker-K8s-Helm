from fastapi import FastAPI
from .api.v1.routes import events, notifications
from .db.session import engine, Base
from .core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# create tables (for dev only; use migrations in prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Notification Service")

# CORS - frontend origin(s) should be added here
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://task.local",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(events.router)
app.include_router(notifications.router)

@app.get("/health")
def health():
    return {"status": "ok", "env": {"database": settings.DATABASE_URL, "redis": settings.REDIS_URL}}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Event Notification Service API\nVisit /docs for API documentation."}

