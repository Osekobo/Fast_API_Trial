from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func, cast, Date
from datetime import timedelta
from models import Base, engine, Product, Sale, User, Purchase, SalesDetails, Payment
from typing import List
from schemas import (
    ProductGetMap,
    ProductPostMap,
    SaleGetMap,
    SalePostMap,
    UserGetRegister,
    UserPostRegister,
    UserPostLogin,
    PurchaseGetMap,
    PurchasePostMap,
    # SalePerProductMap,
    # SaleDetailsItem,
    SalesPerProductOut,
    RemainingPerProductOut,
    ProfitPerProduct,
    ProfitPerDay,
    Token,
    PaymentResponse,
    Item
)
from utils import (
    get_db,
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)


app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30

origins = [
    "http://localhost:5173",  # React app
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create tables on startup
Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    # Base.metadata.drop_all(bind=engine)


@app.get("/")
def read_root():
    return {"Duka FastAPI": "Version 1.0"}


@app.get("/items")
def get_items():
    return [
        {"id": 1, "name": "Laptop", "price": 70000},
        {"id": 2, "name": "Phone", "price": 60000},
    ]


# Register
@app.post("/register", response_model=UserGetRegister)
def register_user(user: UserPostRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")

    new_user = User(
        name=user.name,
        phone=user.phone,
        email=user.email,
        password=get_password_hash(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Login


# @app.post("/login", response_model=Token)
@app.post("/login")
def login_user(user: UserPostLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.scalar(select(User).where(User.email == user.email))
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # return Token(access_token=access_token, token_type="bearer")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )
    # return Token(access_token=access_token, token_type="bearer")
    return {
        "message": "Login successful",
        "user": {
            "email": db_user.email,
            "name": db_user.name
        }
    }


@app.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    print(current_user.email)
    return {"email": current_user.email}


# @app.get("/me")
# async def get_me(
#     current_user: User = Depends(get_current_user)
# ):
#     return {
#         "id": current_user.id,
#         "email": current_user.email,
#     }

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

# @app.get("/admin/applications")
# def get_applications(
#     current_user = Depends(require_admin)
# ):
#     return applications


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token", httponly=True, secure=False, samesite="lax")
    return {"message": "Logout successful"}


@app.get("/users", response_model=list[UserGetRegister])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(select(User)).all()


# Products
@app.get("/products", response_model=list[ProductGetMap])
def get_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Product)).all()


@app.post("/products", response_model=ProductGetMap)
def create_product(product: ProductPostMap,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user),
                   ):
    model = Product(**product.dict())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


# Sales
@app.get("/sales", response_model=list[SaleGetMap])
def get_sales(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Sale)).all()


@app.post("/sales", response_model=SaleGetMap)
def create_sale(
    sale: SalePostMap,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = Sale()

    for item in sale.details:
        model.details.append(
            SalesDetails(
                product_id=item.product_id,
                quantity=item.quantity
            )
        )

    db.add(model)
    db.commit()
    db.refresh(model)
    return model


# Purchases
@app.get("/purchase", response_model=list[PurchaseGetMap])
def get_purchases(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return db.scalars(select(Purchase)).all()


@app.post("/purchase", response_model=PurchaseGetMap, status_code=201)
def create_purchase(
    purchase: PurchasePostMap,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_purchase = Purchase(
        quantity=purchase.quantity,
        product_id=purchase.product_id
    )
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)
    return new_purchase
