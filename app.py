from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException
from typing import Annotated

from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

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


# @app.put("/items/{item_id}")
# async def create_item(id: int, item: Items):
#     data[id] = item.model_dump()
#     return {"message": "ok", "item": data[id]}


# @app.put("/items/{item-Id}")
# async def update_item(item_id: int, item: Annotated[Items, Body(embed=True)]):
#     results = {"item_id": item_id, "item": item}
#     return results
