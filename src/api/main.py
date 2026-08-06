from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.auth import router as auth_router

app = FastAPI(title="Crypto Market Intelligence API", version="0.1.0")

# Allow CORS for your dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Auth Router
app.include_router(auth_router, prefix="/auth", tags=["🔐 Authentication"])

@app.get("/")
def read_root():
    return {"message": "Crypto API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
