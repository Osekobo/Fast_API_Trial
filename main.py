from fastapi import FastAPI, Depends, select, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from flask_bcrypt import check_password_hash, generate_password_hash
from jsonmap import postRegister, getRegister, Token, getProducts, postProducts, getForgotPassword, postForgotpassword, getVerifyOtp, postVerifyOtp, getpassword, postPassword
from models import User, Product, OTP
from datetime import timedelta, datetime, timezone
from myjwt import (get_db, create_access_token,
                   get_current_user, format_phone, generate_otp)
app = FastAPI()
ACCESS = 30


@app.post("/register", response_model=getRegister, status_code=201)
def register(user: postRegister, db: Session = Depends(get_db)):
    if db.scalars(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="User already exists")
    if db.scalars(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    usr = User(name=user.name, phone=user.phone,
               email=user.email, password=generate_password_hash(user.password))
    try:
        db.add(usr)
        db.commit()
        db.refresh(usr)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    email = data.username.lower().strip()
    usr = db.scalars(select(User).where(User.email == email))
    if not usr or not check_password_hash(data.password, usr.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"Bearer": "WWW-Authenticate"})
    token = create_access_token(
        data={"sub": usr.email, "scope": "me items"}, expires_delta=timedelta(minutes=ACCESS))
    return Token(token=token, token_type="bearer")


@app.get("/products", response_model=list[getProducts])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=postProducts, status_code=201)
def create_products(product: postProducts, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = Product(**product.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@app.post("forgot_password", response_model=getForgotPassword, status_code=201)
def forgot_password(data: postForgotpassword, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = None
    contact_type = None
    if data.email:
        email = data.email.lower().strip()
        user = db.scalars(select(User).where(User.email == email))
        contact_type = "email"
    elif data.phone:
        raw_phone = data.phone.strip()
        try:
            phone_formatted = format_phone(raw_phone)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        user = db.scalars(select(User).where(
            User.phone == user.phone_formatted))
        contact_type = "phone"
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")

    if not user:
        return {"message": "If user exists, an OTP has been sent"}

    db.query(select(OTP).filter_by(user_id=user.id)).delete()
    otp_code = generate_otp()
    otp_entry = OTP(user_id=user.id, otp=otp_code,
                    created_on=datetime.now(timezone.utc))
    db.add(otp_entry)
    db.commit()
    return {"message": "If User exists, an OTP has been sent"}


@app.post("/verify_otp", response_model=getVerifyOtp, status_code=201)
def verify_otp(data: postVerifyOtp, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = None
    if data.email:
        
    pass
