import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    idempotency_key = Column(String, unique=True, nullable=False)

    total_revenue = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    total_profit = Column(Numeric(12, 2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_tenant_order_date", "tenant_id", "created_at"),
    )