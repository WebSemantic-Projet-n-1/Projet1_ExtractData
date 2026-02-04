from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/requests/{request_id}")
def read_request(request_id: int, title: str, answer: str):
    return {
        "request_id": request_id,
        "title": title,
        "answer": answer
    }