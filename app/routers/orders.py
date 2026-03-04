from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_tenant
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from fastapi import APIRouter, Depends, BackgroundTasks
from app.services.background_tasks import process_daily_sales

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    tenant_id=Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db),
):
    order = await OrderService.create_order(
        session,
        tenant_id,
        order_data
    )

    return OrderResponse(
        id=order.id,
        total_revenue=order.total_revenue,
        total_cost=order.total_cost,
        total_profit=order.total_profit,
    )


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    background_tasks: BackgroundTasks,
    tenant_id=Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db),
):
    
 order = await OrderService.create_order(session, tenant_id, order_data) 

 background_tasks.add_task(process_daily_sales, tenant_id)

 return OrderResponse(
    id=order.id,
    total_revenue=order.total_revenue,
    total_cost=order.total_cost,
    total_profit=order.total_profit,
 )
