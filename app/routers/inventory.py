from fastapi import APIRouter, Depends
from datetime import date
from pydantic import BaseModel
from uuid import UUID

from app.dependencies.auth import get_current_tenant
from app.core.mongo import inventory_collection

router = APIRouter(prefix="/inventory", tags=["Inventory"])


class InventorySnapshot(BaseModel):
    product_id: UUID
    quantity: int
    snapshot_date: date


@router.post("/snapshot")
async def create_snapshot(
    snapshot: InventorySnapshot,
    tenant_id=Depends(get_current_tenant),
):

    document = {
        "tenant_id": str(tenant_id),
        "product_id": str(snapshot.product_id),
        "quantity": snapshot.quantity,
        "snapshot_date": snapshot.snapshot_date.isoformat(),
    }

    await inventory_collection.insert_one(document)

    return {"message": "Snapshot stored"}