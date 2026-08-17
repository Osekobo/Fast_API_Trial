from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base
import enum


class UserRole(str, enum.Enum):
    APPLICANT = "APPLICANT"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"
    CHIEF = "CHIEF"          # new


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"         # after chief verification
    UNDER_REVIEW = "UNDER_REVIEW"
    NEEDS_INFO = "NEEDS_INFO"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # hashed
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.APPLICANT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Applications where this user is the applicant
    applications = relationship(
        "Application", foreign_keys='Application.user_id', back_populates="user")
    # Applications assigned to this user as reviewer
    assigned_applications = relationship(
        "Application", foreign_keys='Application.assigned_reviewer_id', back_populates="assigned_reviewer")
    # Reviews made by this user
    reviews = relationship("Review", back_populates="reviewer")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    course = Column(String, nullable=False)
    year_of_study = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    assigned_reviewer_id = Column(
        String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Applicant (the user who submitted)
    user = relationship("User", foreign_keys=[
                        user_id], back_populates="applications")
    # Assigned reviewer
    assigned_reviewer = relationship("User", foreign_keys=[
                                     assigned_reviewer_id], back_populates="assigned_applications")
    documents = relationship("Document", back_populates="application")
    reviews = relationship("Review", back_populates="application")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey(
        "applications.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="documents")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey(
        "applications.id"), nullable=False)
    reviewer_id = Column(String, ForeignKey("users.id"), nullable=False)
    # APPROVED, REJECTED, NEEDS_INFO
    recommendation = Column(String, nullable=False)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
