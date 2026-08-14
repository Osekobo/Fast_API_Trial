from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from schemas import GetRegister, PostRegister
from models import User, db
from utils import (get_db)
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"version": "1.0"}


# @app.get("/products")
# def get_products(prod: GetProduct):
#     if not all in ():
#         raise HTTPException(
#             detail="Ensure all fields are set", status_code=400)
#     pass


# @app.post("/products")
# def create_products():
#     pass

class Item(BaseModel):
    id: int
    name: str
    price: float


@app.get("/items")
def get_items():
    return [
        {"id": 1, "name": "Laptop", "price": 70000},
        {"id": 2, "name": "Phone", "price": 60000},
    ]


@app.post("/register", response_model=GetRegister)
def register_user(user: PostRegister, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == user.email)):
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.scalar(select(User).where(User.phone == user.phone)):
        raise HTTPException(status_code=400, detail="Phone already registered")
    new_user = User(name=user.name, phone=user.phone, email=user.email)
    pass
