from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database.database import Base

return_sale_association = Table(
    "return_sale_association",
    Base.metadata,
    Column("sale_transaction_id", Integer, ForeignKey("sale_transactions.sale_transaction_id", ondelete="CASCADE"), primary_key=True),
    Column("return_transaction_id", Integer, ForeignKey("return_transactions.return_transaction_id", ondelete="CASCADE"), primary_key=True),
)


