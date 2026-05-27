from datetime import date

from pydantic import BaseModel


class DataCreate(BaseModel):
    data: dict

class DataOut(BaseModel):
    data: str
