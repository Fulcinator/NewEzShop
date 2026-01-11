from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base


order_productType_association = Table(
    "order_productType_association",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True),
    Column("product_type_id", Integer, ForeignKey("product_types.product_type_id", ondelete="CASCADE"), primary_key=True),
)