from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models import Application, User, Document, ApplicationStatus, UserRole
from ..schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut, DocumentOut, StatsOut,DocumentCreate
from ..dependencies import role_required, get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])

# ─── LIST applications (role‑based) ───
@router.get("/", response_model=list[ApplicationOut])
async def get_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.ADMIN:
        # Admin sees all applications
        result = await db.execute(select(Application))
    elif current_user.role == UserRole.REVIEWER:
        # Reviewer sees only assigned apps that are VERIFIED or UNDER_REVIEW
        result = await db.execute(
            select(Application)
            .where(
                Application.assigned_reviewer_id == current_user.id,
                Application.status.in_([ApplicationStatus.VERIFIED, ApplicationStatus.UNDER_REVIEW])
            )
        )
    elif current_user.role == UserRole.CHIEF:
        # Chief sees all PENDING applications (to verify)
        result = await db.execute(
            select(Application).where(Application.status == ApplicationStatus.PENDING)
        )
    else:
        # Applicant sees own applications
        result = await db.execute(
            select(Application).where(Application.user_id == current_user.id)
        )
    return result.scalars().all()


# ─── GET single application ───
@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Access control
    if current_user.role == UserRole.ADMIN:
        pass  # admin can see any
    elif current_user.role == UserRole.CHIEF:
        if app.status != ApplicationStatus.PENDING:
            raise HTTPException(status_code=403, detail="Chief can only view pending applications")
    elif current_user.role == UserRole.REVIEWER:
        if app.assigned_reviewer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to you")
        if app.status not in [ApplicationStatus.VERIFIED, ApplicationStatus.UNDER_REVIEW]:
            raise HTTPException(status_code=403, detail="Application not ready for review")
    else:  # applicant
        if app.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    return app


# ─── CREATE application (applicant only) ───
@router.post("/", response_model=ApplicationOut)
async def create_application(
    app_data: ApplicationCreate,
    current_user: User = Depends(role_required([UserRole.APPLICANT])),
    db: AsyncSession = Depends(get_db)
):
    new_app = Application(
        user_id=current_user.id,
        full_name=app_data.full_name,
        phone=app_data.phone,
        institution=app_data.institution,
        course=app_data.course,
        year_of_study=app_data.year_of_study,
        amount=app_data.amount,
        status=ApplicationStatus.PENDING
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return new_app


# ─── UPDATE application (admin only) ───
# Used to assign reviewer and change status (admin can set VERIFIED, but chief does it separately)
@router.put("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: str,
    update_data: ApplicationUpdate,
    current_user: User = Depends(role_required([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if update_data.status is not None:
        # Admin can set any status, but typically they'll set to UNDER_REVIEW or APPROVED/REJECTED
        app.status = update_data.status
    if update_data.assigned_reviewer_id is not None:
        app.assigned_reviewer_id = update_data.assigned_reviewer_id
    await db.commit()
    await db.refresh(app)
    return app


# ─── CHIEF VERIFICATION ───
@router.put("/{app_id}/verify")
async def verify_application(
    app_id: str,
    current_user: User = Depends(role_required([UserRole.CHIEF])),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if app.status != ApplicationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending applications can be verified")
    app.status = ApplicationStatus.VERIFIED
    await db.commit()
    await db.refresh(app)
    return {"message": "Application verified by chief", "application": app}


# ─── DOCUMENTS ───
@router.post("/documents", response_model=DocumentOut)
async def upload_document(
    doc_data: DocumentCreate,
    current_user: User = Depends(role_required([UserRole.APPLICANT])),
    db: AsyncSession = Depends(get_db)
):
    # Check that the application belongs to the current user
    result = await db.execute(select(Application).where(Application.id == doc_data.application_id))
    app = result.scalar_one_or_none()
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload for this application")
    new_doc = Document(
        application_id=doc_data.application_id,
        file_name=doc_data.file_name,
        file_url=doc_data.file_url
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    return new_doc


@router.get("/documents", response_model=list[DocumentOut])
async def get_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get documents for user's applications (or all if admin)
    if current_user.role == UserRole.ADMIN:
        result = await db.execute(select(Document))
    else:
        subquery = select(Application.id).where(Application.user_id == current_user.id)
        result = await db.execute(select(Document).where(Document.application_id.in_(subquery)))
    return result.scalars().all()


# ─── STATS ───
@router.get("/stats", response_model=StatsOut)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.ADMIN:
        total = await db.execute(select(func.count()).select_from(Application))
        pending = await db.execute(select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.PENDING))
        verified = await db.execute(select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.VERIFIED))
        approved = await db.execute(select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.APPROVED))
        approved_apps = await db.execute(select(Application.amount).where(Application.status == ApplicationStatus.APPROVED))
        disbursed = sum([a[0] for a in approved_apps.all()]) or 0.0
    elif current_user.role == UserRole.CHIEF:
        # Chief only sees pending count
        total = await db.execute(select(func.count()).select_from(Application).where(Application.status == ApplicationStatus.PENDING))
        pending = total
        verified = 0
        approved = 0
        disbursed = 0.0
    elif current_user.role == UserRole.REVIEWER:
        total = await db.execute(
            select(func.count()).select_from(Application)
            .where(Application.assigned_reviewer_id == current_user.id)
        )
        pending = await db.execute(
            select(func.count()).select_from(Application)
            .where(
                Application.assigned_reviewer_id == current_user.id,
                Application.status == ApplicationStatus.UNDER_REVIEW
            )
        )
        verified = 0
        approved = 0
        disbursed = 0.0
    else:  # applicant
        total = await db.execute(select(func.count()).select_from(Application).where(Application.user_id == current_user.id))
        pending = await db.execute(
            select(func.count()).select_from(Application)
            .where(Application.user_id == current_user.id, Application.status == ApplicationStatus.PENDING)
        )
        approved = await db.execute(
            select(func.count()).select_from(Application)
            .where(Application.user_id == current_user.id, Application.status == ApplicationStatus.APPROVED)
        )
        approved_apps = await db.execute(
            select(Application.amount)
            .where(Application.user_id == current_user.id, Application.status == ApplicationStatus.APPROVED)
        )
        disbursed = sum([a[0] for a in approved_apps.all()]) or 0.0

    return StatsOut(
        total=total.scalar() or 0,
        pending=pending.scalar() or 0,
        approved=approved.scalar() or 0,
        disbursed=disbursed
    )