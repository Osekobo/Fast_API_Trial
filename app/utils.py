from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from pwdlib import PasswordHash

from models import SessionLocal, User


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


# =========================
# PASSWORD HASHING
# =========================

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using Argon2.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against its stored hash.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# USER FUNCTIONS
# =========================

def get_user_by_email(
    db: Session,
    email: str
):
    """
    Find a user by email.
    """
    return db.scalar(
        select(User).where(User.email == email)
    )


# =========================
# CREATE JWT ACCESS TOKEN
# =========================

def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = (
            datetime.now(timezone.utc)
            + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# =========================
# GET CURRENT USER
# =========================

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # -------------------------
    # Get token from cookie
    # -------------------------

    token = request.cookies.get("access_token")

    print("TOKEN:", token)

    if not token:
        raise credentials_exception

    # -------------------------
    # Decode JWT
    # -------------------------

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD:", payload)

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except InvalidTokenError as e:

        print("JWT ERROR:", e)

        raise credentials_exception

    # -------------------------
    # Find user in database
    # -------------------------

    user = get_user_by_email(
        db,
        email
    )

    if user is None:
        raise credentials_exception

    return user