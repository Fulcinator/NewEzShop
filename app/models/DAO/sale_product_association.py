from sqlalchemy import Table, Column, Integer, ForeignKey, Float
from app.database.database import Base

sale_product_association = Table(
    "sale_product_association",
    Base.metadata,
    Column("sale_transaction_id", Integer, ForeignKey("sale_transactions.sale_transaction_id", ondelete="CASCADE"), primary_key=True),
    Column("product_type_id", Integer, ForeignKey("product_types.product_type_id", ondelete="CASCADE"), primary_key=True),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Float, nullable=False),
    Column("discount_rate", Float, nullable=False, default=0.0),
)



