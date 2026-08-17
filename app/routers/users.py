from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import User, UserRole
from ..schemas import UserOut
from ..dependencies import role_required

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserOut])
async def get_users(current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.put("/{user_id}", response_model=UserOut)
async def update_user_role(user_id: str, role: UserRole, current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user