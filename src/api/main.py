from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes.auth import router as auth_router
from src.api.routes.prices import router as prices_router
from src.core.database.connection import init_db

# Initialize database
init_db()

app = FastAPI(
    title="Crypto Market Intelligence Platform",
    description="Enterprise-grade crypto market intelligence with AI/ML and security",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(prices_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "crypto-market-intelligence",
        "version": "0.1.0",
        "environment": os.getenv("APP_ENV", "development")
    }

@app.get("/")
async def root():
    return {
        "service": "Crypto Market Intelligence Platform",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "status": "operational"
    }

print("🚀 Application ready!")