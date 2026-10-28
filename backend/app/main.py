import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import init_db
from app.services.seed_data import seed_database
from app.api.routes import router as api_router

app = FastAPI(
    title="Invoice Extraction & Approval Agent API",
    description="Agent trích xuất hóa đơn và đối chiếu rule engine để ra quyết định phê duyệt thanh toán (APPROVE | REVIEW | REJECT)",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

# Mount API
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "service": "Invoice Extraction & Approval Agent",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
