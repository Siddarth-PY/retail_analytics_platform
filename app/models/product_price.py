import uuid
from sqlalchemy import Column, Date, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    effective_from = Column(Date, nullable=False)

    __table_args__ = (
        Index("idx_product_effective", "product_id", "effective_from"),
    )