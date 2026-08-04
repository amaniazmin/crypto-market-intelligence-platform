from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import os
import jwt
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

users = {}

class UserRole:
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = UserRole.VIEWER

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(user_id: str, username: str, role: str) -> str:
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "exp": expires,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
async def register(request: RegisterRequest):
    for user in users.values():
        if user["username"] == request.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if user["email"] == request.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = f"user_{len(users) + 1}"
    users[user_id] = {
        "id": user_id,
        "username": request.username,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "role": request.role or UserRole.VIEWER
    }
    
    return {
        "message": "User created successfully",
        "user": {
            "id": user_id,
            "username": request.username,
            "email": request.email,
            "role": request.role or UserRole.VIEWER
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = None
    for u in users.values():
        if u["username"] == request.username:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )
    
    return TokenResponse(access_token=token)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        user = users.get(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(required_role: str):
    async def _require_role(user = Depends(get_current_user)):
        if user["role"] != required_role and user["role"] != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail=f"Required role: {required_role}")
        return user
    return _require_role

@router.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    """
    Get the current user's profile.
    Requires authentication.
    """
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"]
    }

@router.get("/admin-only")
async def admin_only(user = Depends(require_role(UserRole.ADMIN))):
    """
    Admin-only endpoint.
    Only users with admin role can access.
    """
    return {
        "message": "Welcome, Admin!",
        "user": user["username"],
        "role": user["role"]
    }

# Create default users
users["user_1"] = {
    "id": "user_1",
    "username": "admin",
    "email": "admin@example.com",
    "password_hash": hash_password("Admin@123"),
    "role": UserRole.ADMIN
}
users["user_2"] = {
    "id": "user_2",
    "username": "analyst",
    "email": "analyst@example.com",
    "password_hash": hash_password("Analyst@123"),
    "role": UserRole.ANALYST
}
users["user_3"] = {
    "id": "user_3",
    "username": "viewer",
    "email": "viewer@example.com",
    "password_hash": hash_password("Viewer@123"),
    "role": UserRole.VIEWER
}
