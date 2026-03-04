from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product_price import ProductPrice
from app.repositories.order_repository import OrderRepository




class OrderService:

    @staticmethod
    async def create_order(session: AsyncSession, tenant_id, order_data):

        async with session.begin():

            # Check idempotency inside transaction
            existing_order = await OrderRepository.get_by_idempotency_key(
                session,
                order_data.idempotency_key
            )

            if existing_order:
                return existing_order

            total_revenue = 0
            total_cost = 0

            order = Order(
                tenant_id=tenant_id,
                idempotency_key=order_data.idempotency_key,
                total_revenue=0,
                total_cost=0,
                total_profit=0,
            )

            await OrderRepository.create(session, order)

            for item in order_data.items:

                result = await session.execute(
                    select(ProductPrice)
                    .where(ProductPrice.product_id == item.product_id)
                    .order_by(desc(ProductPrice.effective_from))
                    .limit(1)
                )

                price = result.scalar_one_or_none()

                if not price:
                    raise ValueError("Product price not found")

                revenue = price.selling_price * item.quantity
                cost = price.cost_price * item.quantity

                total_revenue += revenue
                total_cost += cost

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=price.selling_price,
                    unit_cost=price.cost_price,
                )

                session.add(order_item)

            order.total_revenue = total_revenue
            order.total_cost = total_cost
            order.total_profit = total_revenue - total_cost

        return order