from fastapi import FastAPI, Depends, select, HTTPException, status
from jsonmap import userGetRegister, userPostRegister, Token, userGetproduct, userPostProduct, getForgotPassword, postForgotPassword, getVerifyOtp, postVerifyOtp
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from werkzeug.security import check_password_hash, generate_password_hash
from myjwt import get_db, create_access_token, get_current_user, phone_format, generate_otp
from models import User, Product, Purchase, Sale, OTP
from datetime import datetime
app = FastAPI()

ACCESS_TIME = 40


@app.post("/register", reponse_reponse=userGetRegister, status_code=201)
def register(user: userPostRegister, db: Session = Depends(get_db)):
    if db.scalars(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalars(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    usr = User(name=user.name, phone=user.phone, email=user.email,
               password=generate_password_hash(user.password))
    try:
        db.add(usr)
        db.commit()
        db.refresh(usr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="User registration failed")


@app.post("/login", response_model=Token)
def login(data: OAuth2PasswordBearer, db: Session = Depends(get_db)):
    email = data.username.lower().strip()
    usr = db.scalars(select(User).where(User.email == email))
    if not usr or not check_password_hash(data.password, usr.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invaid email or password", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(
        data={"sub": "usr.email", "scope": "me items"}, expire_delta=datetime(minute=ACCESS_TIME))
    return Token(token=token, token_type="bearer")


@app.get("/products", response_model=list[userGetproduct])
def get_products(db: Product = Session(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=userGetproduct, status_code=201)
def create_products(product: userPostProduct, db: Session = Depends(get_db), current_user: Session = Depends(get_current_user)):
    model = Product(**product.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@app.post("/forgot_password", response_model=getForgotPassword, status_code=201)
def forgot_password(data: postForgotPassword, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = None
    contact_type = None
    if data.email:
        email = data.email.lower().strip()
        user = db.scalars(select(User).where(User.email == email))
        contact_type = "email"
    elif data.phone:
        raw_phone = data.phone.strip()
        try:
            formatted_phone = phone_format(raw_phone)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        usr = db.scalar(select(User).where(User.phone == formatted_phone))
        contact_type = "phone"
    else:
        raise HTTPException(status_code=400, detail="Email or phone required")
    if not usr:
        return {"message": "If User exists, an OTP has been sent"}
    db.query(OTP).filter_by(user_id=usr.id).delete()
    otp_code = generate_otp()
    otp_entry = OTP()
    db.add(otp_entry)
    db.commit()
    return {"message": "If user exists, an OTP has been sent"}


@app.post("/verify_otp", response_model=getVerifyOtp, status_code=201)
def verify_otp(data: postVerifyOtp, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    email = data.username.lower().strip()
    otp = data.otp.strip()
    usr = db.scalars(select(User.email == email))
    if not usr:
        raise HTTPException(status_code=400, detail="Use not found")
    if not otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    pass
