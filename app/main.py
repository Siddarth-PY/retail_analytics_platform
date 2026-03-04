from fastapi import FastAPI, Depends
from app.core.database import engine, Base
from app.dependencies.auth import get_current_user
from app.routers import auth
from app.routers import orders
from app.routers import analytics
from app.routers import inventory

app = FastAPI(title="Multi-Tenant Retail Analytics API")

app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(inventory.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root(user=Depends(get_current_user)):
    return {"message": "Authenticated", "user": user}