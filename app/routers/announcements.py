from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Announcement, User, UserRole
from ..schemas import AnnouncementCreate, AnnouncementOut
from ..dependencies import role_required

router = APIRouter(prefix="/announcements", tags=["announcements"])

@router.get("/", response_model=list[AnnouncementOut])
async def get_announcements(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Announcement).order_by(Announcement.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=AnnouncementOut)
async def create_announcement(data: AnnouncementCreate, current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    new_ann = Announcement(
        title=data.title,
        content=data.content,
        created_by=current_user.id
    )
    db.add(new_ann)
    await db.commit()
    await db.refresh(new_ann)
    return new_ann

@router.delete("/{ann_id}")
async def delete_announcement(ann_id: str, current_user: User = Depends(role_required([UserRole.ADMIN])), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(ann)
    await db.commit()
    return {"message": "Deleted"}