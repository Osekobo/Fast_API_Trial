from fastapi import FastAPI
app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello world!"}


@app.get("/items/{item_id}")
def read_item(item_id:int):
    return {"Item id": item_id}
