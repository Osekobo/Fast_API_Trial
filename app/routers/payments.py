from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User, UserRole
from ..dependencies import role_required

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/")
async def get_payments(current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    # Replace with real DB query later
    return [
        {"id": "1", "applicant": "John Doe", "amount": 50000, "date": "2026-08-15", "status": "COMPLETED"},
        {"id": "2", "applicant": "Jane Smith", "amount": 75000, "date": "2026-08-14", "status": "PENDING"},
    ]