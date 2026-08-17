from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserCreate, UserLogin, UserOut
from ..auth import get_password_hash, verify_password, create_access_token
from ..dependencies import role_required

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    token = create_access_token(data={"sub": new_user.id})
    return {
        "token": token,
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "firstName": new_user.first_name,
            "lastName": new_user.last_name,
            "role": new_user.role,
            "createdAt": new_user.created_at.isoformat() if new_user.created_at else None
        }
    }

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.id})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "role": user.role,
            "createdAt": user.created_at.isoformat() if user.created_at else None
        }
    }

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(role_required([UserRole.APPLICANT, UserRole.REVIEWER, UserRole.ADMIN]))):
    return current_user