import uuid
from sqlalchemy import Column, ForeignKey, Integer, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)

    __table_args__ = (
        Index("idx_order_product", "order_id", "product_id"),
    )