from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .models import UserRole, ApplicationStatus

# --- User schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    role: Optional[UserRole] = UserRole.APPLICANT

    class Config:
        populate_by_name = True          # allows both 'first_name' and 'firstName'
        use_enum_values = True           # send enum values as strings in responses

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True           # for SQLAlchemy ORM conversion

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str

# --- Application schemas ---
class ApplicationCreate(BaseModel):
    full_name: str = Field(..., alias="fullName")
    phone: str
    institution: str
    course: str
    year_of_study: int = Field(..., alias="yearOfStudy")
    amount: float

    class Config:
        populate_by_name = True

class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    assigned_reviewer_id: Optional[str] = Field(None, alias="assignedReviewerId")

    class Config:
        populate_by_name = True

class ApplicationOut(BaseModel):
    id: str
    user_id: str
    full_name: str
    phone: str
    institution: str
    course: str
    year_of_study: int
    amount: float
    status: ApplicationStatus
    assigned_reviewer_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Document schemas ---
class DocumentCreate(BaseModel):
    application_id: str = Field(..., alias="applicationId")
    file_name: str = Field(..., alias="fileName")
    file_url: str = Field(..., alias="fileUrl")

    class Config:
        populate_by_name = True

class DocumentOut(BaseModel):
    id: str
    application_id: str
    file_name: str
    file_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# --- Review schemas ---
class ReviewCreate(BaseModel):
    recommendation: str
    comments: Optional[str] = None

class ReviewOut(BaseModel):
    id: str
    application_id: str
    reviewer_id: str
    recommendation: str
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Announcement schemas ---
class AnnouncementCreate(BaseModel):
    title: str
    content: str

class AnnouncementOut(BaseModel):
    id: str
    title: str
    content: str
    created_by: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Stats ---
class StatsOut(BaseModel):
    total: int
    pending: int
    approved: int
    disbursed: float

class AdminStatsOut(BaseModel):
    users: int
    applications: int
    pending: int
    disbursed: float