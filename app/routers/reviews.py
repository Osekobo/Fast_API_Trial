from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Review, Application, User, UserRole, ApplicationStatus
from ..schemas import ReviewCreate, ReviewOut
from ..dependencies import role_required

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/{application_id}", response_model=ReviewOut)
async def submit_review(application_id: str, review_data: ReviewCreate, current_user: User = Depends(role_required([UserRole.REVIEWER, UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    # Check application exists and is assigned to current user (if reviewer)
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if current_user.role != UserRole.ADMIN and app.assigned_reviewer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to you")
    
    new_review = Review(
        application_id=application_id,
        reviewer_id=current_user.id,
        recommendation=review_data.recommendation,
        comments=review_data.comments
    )
    db.add(new_review)
    
    # Update application status based on recommendation
    if review_data.recommendation == "APPROVED":
        app.status = ApplicationStatus.APPROVED
    elif review_data.recommendation == "REJECTED":
        app.status = ApplicationStatus.REJECTED
    elif review_data.recommendation == "NEEDS_INFO":
        app.status = ApplicationStatus.NEEDS_INFO
    await db.commit()
    await db.refresh(new_review)
    return new_review

@router.get("/{application_id}", response_model=list[ReviewOut])
async def get_reviews(application_id: str, current_user: User = Depends(role_required([UserRole.ADMIN, UserRole.REVIEWER])), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.application_id == application_id))
    return result.scalars().all()