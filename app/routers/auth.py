from fastapi import APIRouter
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login():
    # For now, dummy login (we improve later)
    token = create_access_token(
        {
            "user_id": "demo-user",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "role": "admin",
        }
    )
    return {"access_token": token}