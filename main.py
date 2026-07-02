from fastapi import FastAPI
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
