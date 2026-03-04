from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import uvicorn
from .database import engine, Base, get_db
from . import models

# Crear tablas en PostgreSQL al iniciar (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BISP API", 
    description="Business Intelligence Scraper Platform API", 
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to BISP API. System is up and running."}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Basic check to see if DB is reachable
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status, "redis": "pending"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
