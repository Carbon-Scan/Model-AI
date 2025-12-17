from pydantic import BaseModel
from typing import List

class CarbonItem(BaseModel):
    produk: str
    berat_kg: float

class CarbonRequest(BaseModel):
    items: List[CarbonItem]

class CarbonResponse(BaseModel):
    detail: list
    total_karbon: float
