from fastapi import FastAPI, Query, HTTPException
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello world!"}


mock_data = {1: {"name": "13kg Gas Refill", "price": 2500.0, "is_stock": True},
             2: {"name": "6kg Gas Refill", "price": 1200.0, "is_stock": True}
             }


@app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
def read_item(user_id: str):
    return {"Item id": user_id}


@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.get("/items/{item_id}")
def get_items(item_id: int):
    item = mock_data.get(item_id)
    if item is None:
        raise HTTPException(
            status_code=404, detail=f"Item with ID {item_id} does not exist")
    return {"id": item_id, "data": item}
    # return mock_data


@app.post("/items/", status_code=201)
def create_item(prod: Item):
    new_id = max(mock_data.keys())+1 if mock_data else 1
    item_dict = prod.model_dump()
    mock_data[new_id] = item_dict
    return {"id": new_id, "data": item_dict}


@app.post("/item/")
async def read_items(q: Annotated[str | None, Query(min_length=4, max_length=50, pattern="^fixedquery$")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
