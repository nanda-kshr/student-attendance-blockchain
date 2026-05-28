from datetime import date

from pydantic import BaseModel


class DataCreate(BaseModel):
    data: dict

class SearchIndex(BaseModel):
    index: str

class SearchOut(BaseModel):
    data: list[dict] | dict | None

class DataOut(BaseModel):
    data: str
