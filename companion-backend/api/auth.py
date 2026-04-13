from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from auth import verify_password, get_password_hash, create_access_token, get_current_user
from models import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    pool = await get_db()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1 OR username = $2", user.email, user.username)
        if existing:
            raise HTTPException(status_code=400, detail="Email or username already registered")
        
        hashed_password = get_password_hash(user.password)
        result = await conn.fetchrow(
            "INSERT INTO users (email, username, hashed_password, full_name) VALUES ($1, $2, $3, $4) RETURNING id, email, username, full_name, created_at",
            user.email, user.username, hashed_password, user.full_name
        )
        return result

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    pool = await get_db()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE username = $1", form_data.username)
        
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user