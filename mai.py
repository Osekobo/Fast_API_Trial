from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from schemas import GetProduct
# from models import db
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
