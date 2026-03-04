from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from app.core.database import get_db
from app.dependencies.auth import get_current_tenant
from app.models.order import Order
from sqlalchemy import func
from datetime import timedelta
from sqlalchemy import func
from app.models.order_item import OrderItem
from app.core.mongo import inventory_collection

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/profitability")
async def profitability(
    from_date: date = Query(...),
    to_date: date = Query(...),
    tenant_id=Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db),
):

    stmt = (
        select(
            func.coalesce(func.sum(Order.total_revenue), 0).label("revenue"),
            func.coalesce(func.sum(Order.total_cost), 0).label("cost"),
        )
        .where(Order.tenant_id == tenant_id)
        .where(Order.created_at >= from_date)
        .where(Order.created_at <= to_date)
    )

    result = await session.execute(stmt)
    row = result.one()

    revenue = float(row.revenue)
    cost = float(row.cost)
    gross_profit = revenue - cost
    gross_margin = (gross_profit / revenue * 100) if revenue > 0 else 0

    return {
        "revenue": revenue,
        "cost": cost,
        "gross_profit": gross_profit,
        "gross_margin_percentage": round(gross_margin, 2),
    }


@router.get("/demand-trend")
async def demand_trend(
    from_date: date = Query(...),
    to_date: date = Query(...),
    tenant_id=Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db),
):

    # Current period
    current_stmt = (
        select(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_revenue).label("revenue"),
        )
        .where(Order.tenant_id == tenant_id)
        .where(Order.created_at >= from_date)
        .where(Order.created_at <= to_date)
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )

    current_result = await session.execute(current_stmt)
    current_data = {row.day: float(row.revenue) for row in current_result}

    # Previous year period
    prev_from = from_date.replace(year=from_date.year - 1)
    prev_to = to_date.replace(year=to_date.year - 1)

    prev_stmt = (
        select(
            func.date(Order.created_at).label("day"),
            func.sum(Order.total_revenue).label("revenue"),
        )
        .where(Order.tenant_id == tenant_id)
        .where(Order.created_at >= prev_from)
        .where(Order.created_at <= prev_to)
        .group_by(func.date(Order.created_at))
    )

    prev_result = await session.execute(prev_stmt)
    prev_data = {row.day.replace(year=row.day.year + 1): float(row.revenue) for row in prev_result}

    response = []

    for day, revenue in current_data.items():
        prev_revenue = prev_data.get(day, 0)
        growth = (
            ((revenue - prev_revenue) / prev_revenue * 100)
            if prev_revenue > 0
            else 100
        )

        response.append(
            {
                "date": day,
                "revenue": revenue,
                "previous_year_revenue": prev_revenue,
                "growth_percentage": round(growth, 2),
            }
        )

    return response

@router.get("/inventory-depletion")
async def inventory_depletion(
    tenant_id=Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db),
):

    #  Get latest inventory snapshot from Mongo
    snapshot = await inventory_collection.find_one(
        {"tenant_id": str(tenant_id)},
        sort=[("snapshot_date", -1)]
    )

    if not snapshot:
        return {"message": "No inventory snapshot found"}

    product_id = snapshot["product_id"]
    quantity = snapshot["quantity"]

    # Calculate average daily sales from PostgreSQL
    stmt = (
        select(
            func.sum(OrderItem.quantity),
            func.count(func.distinct(func.date(Order.created_at)))
        )
        .join(Order, Order.id == OrderItem.order_id)
        .where(OrderItem.product_id == product_id)
        .where(Order.tenant_id == tenant_id)
    )

    result = await session.execute(stmt)
    total_sales, active_days = result.one()

    if not total_sales or not active_days:
        return {"message": "Not enough sales data"}

    avg_daily_sales = total_sales / active_days

    days_to_stockout = quantity / avg_daily_sales

    return {
        "product_id": product_id,
        "current_inventory": quantity,
        "avg_daily_sales": round(avg_daily_sales, 2),
        "estimated_days_to_stockout": round(days_to_stockout, 2),
    }