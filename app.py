from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

data = {1: {"name": "Laptop", "Price": 30000},
        2: {"name": "Computer", "Price": 40000}}


class Items(BaseModel):
    id: int
    name: str
    price: int
    description: str | None = None


@app.get("/")
async def home():
    return {"Version": "1.0"}


@app.get("/items/{item_id}")
async def get_items(id: int):
    return data[id]


@app.put("/items/{item_id}")
async def create_item(id: int, item: Items):
    data[id] = item.model_dump()
    return {"message": "ok", "item": data[id]}
