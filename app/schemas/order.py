from pydantic import BaseModel
from typing import List
from uuid import UUID


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int


class OrderCreate(BaseModel):
    idempotency_key: str
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: UUID
    total_revenue: float
    total_cost: float
    total_profit: float