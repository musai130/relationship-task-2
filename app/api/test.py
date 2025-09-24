import os
from typing import Annotated, Literal
from uuid import uuid4
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from fastapi.responses import HTMLResponse
from models.test import FilterParams, FormData, Item, PersonParams
from config import settings
router = APIRouter(
    tags=["Test"],
    prefix=settings.url.test,
)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
def index():
    return {"message": "Hello, World!"}

@router.post("/items-body/")
async def create_item(item: Item):
    return item

@router.get("/items-query/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

@router.get("/items-path/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@router.get("/items-parameter/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@router.put("/items-nested/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    print(password)
    return {"username": username}

@router.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data

@router.post("/to-tree/")
async def to_treed(
    person: PersonParams = Depends(),
    format: Literal["json", "html"] = Query("json"),
):
    if format == "json":
        return person

    html_content = f"""
    <html>
    <body>
        <h1 style="color: blue;">Данные пользователя</h1>
        <p><span style="color: green;">Имя:</span> <span style="color: red;">{person.first_name}</span></p>
        <p><span style="color: green;">Фамилия:</span> <span style="color: red;">{person.last_name}</span></p>
        <p><span style="color: green;">Пол:</span> <span style="color: red;">{person.sex}</span></p>
        <p><span style="color: green;">Возраст:</span> <span style="color: red;">{person.age}</span></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    allowed_types = ["image/png", "image/jpeg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Неподдерживаемый формат. Разрешены только PNG, JPG, WEBP.",
        )

    ext = file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    file_url = f"/static/uploads/{filename}"
    return {"url": file_url}