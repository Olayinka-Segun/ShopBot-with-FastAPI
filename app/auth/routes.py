from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.utils import create_access_token, hash_password, verify_password
from app.models import User
from database import get_db
from pydantic import BaseModel
from datetime import timedelta
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(request: Request, user: UserRegister, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(
        "SELECT * FROM users WHERE email = :email", {"email": user.email}
    )
    existing_user = existing_user.scalars().first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Redirect to the login page after successful registration
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        "SELECT * FROM users WHERE email = :email", {"email": user.email}
    )
    existing_user = result.scalars().first()

    if not existing_user or not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": existing_user.email}, expires_delta=access_token_expires)

    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

