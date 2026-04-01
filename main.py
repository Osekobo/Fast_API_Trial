from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import User, Product, Purchase, Sale
from jsonmap import userGetRegister, userPostRegister, Token, userGetProducts, userPostProducts, userGetPurchase, userPostPurchase, userGetSales, userPostSales
from werkzeug.security import check_password_hash, generate_password_hash
from myjwt import get_db, get_current_user, create_access_token
from datetime import timedelta
app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/register", response_model=userGetRegister, status_code=201)
def register(user: userPostRegister, db: Session = Depends(get_db)):
    if db.scalars(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalars(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    usr = User(name=user.name, phone=user.phone,
               email=user.email, password=generate_password_hash(user.password))
    try:
        db.add(usr)
        db.commit()
        db.refresh(usr)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="User registration failed")
    return usr


@app.post("/login", response_model=Token)
def login(data: OAuth2PasswordRequestForm, db: Session = Depends(get_db)):
    email = data.username.lower().strip()
    usr = db.scalars(select(User).where(User.email == email))
    if not usr or not check_password_hash(data.password, usr.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(data={"sub": usr.email, "scope": "me items"}, expiry_delta=timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(token=token, token_type="bearer")


@app.get("/products", response_model=list[userGetProducts])
def get_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=userGetProducts, status_code=201)
def create_products(product: userPostProducts, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = Product(**product.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@app.get("/purchase", response_model=list[userGetPurchase])
def get_purchase(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(select(Purchase).where(Purchase.user_id == current_user.id)).all()


@app.post("/purchase", response_model=userPostPurchase, status_code=201)
def create_purchase(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_purchase = Purchase()
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)
    return new_purchase
