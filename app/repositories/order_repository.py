from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order


class OrderRepository:

    @staticmethod
    async def get_by_idempotency_key(
        session: AsyncSession,
        idempotency_key: str
    ):
        result = await session.execute(
            select(Order).where(Order.idempotency_key == idempotency_key)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, order: Order):
        session.add(order)
        await session.flush()  # ensures ID generated
        return order