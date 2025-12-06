from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from typing import TYPE_CHECKING
from app.database.database import Base

if TYPE_CHECKING:
    from .saleTransaction_dao import SaleTransactionDAO


class SaleProductAssociation(Base):
    __tablename__ = "sale_product_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sale_transaction_id = Column(Integer, ForeignKey("sale_transactions.sale_transaction_id", ondelete="CASCADE"), nullable=False)
    product_type_id = Column(Integer, ForeignKey("product_types.product_type_id", ondelete="CASCADE"), nullable=False)
    product_barcode = Column(String(14), nullable=False)  # Barcode for API responses
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount_rate = Column(Float, nullable=False, default=0.0)

    # Relationship back to parent sale
    sale: Mapped["SaleTransactionDAO"] = relationship(
        "SaleTransactionDAO",
        back_populates="lines"
    )



