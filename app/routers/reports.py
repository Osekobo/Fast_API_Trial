from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models import Application, UserRole, ApplicationStatus
from ..schemas import AdminStatsOut
from ..dependencies import role_required
from ..models import User

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary", response_model=AdminStatsOut)
async def get_summary(current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    users = await db.execute(select(func.count()).select_from(User))
    applications = await db.execute(select(func.count()).select_from(Application))
    pending = await db.execute(select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.PENDING))
    approved_apps = await db.execute(select(Application.amount).where(Application.status == ApplicationStatus.APPROVED))
    disbursed = sum([a[0] for a in approved_apps.all()]) or 0.0
    return AdminStatsOut(
        users=users.scalar() or 0,
        applications=applications.scalar() or 0,
        pending=pending.scalar() or 0,
        disbursed=disbursed
    )