from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

return_productType_association = Table(
    "return_productType_association",
    Base.metadata,
    Column("return_transaction_id", Integer, ForeignKey("return_transactions.return_transaction_id", ondelete="CASCADE"), primary_key=True),
    Column("product_type_id", Integer, ForeignKey("product_types.product_type_id", ondelete="CASCADE"), primary_key=True),
)