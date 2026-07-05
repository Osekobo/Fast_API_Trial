from fastapi import FastAPI, Query
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello world!"}


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


@app.post("/items/")
async def read_items(q: Annotated[str | None, Query(min_length=4, max_length=50, pattern="^fixedquery$")] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
