from typing import Union, Any
from fastapi import FastAPI
from app.geofencing_subscriptions import subscriptions

app = FastAPI()

app.include_router(subscriptions.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None) -> dict[str, Any]:
    return {"item_id": item_id, "q": q}
