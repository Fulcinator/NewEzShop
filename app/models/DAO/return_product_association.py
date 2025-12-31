from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship
from app.database.database import Base

class ReturnProductAssociation(Base):
    """Return line item - individual product returned.
    
    Maps swagger ReturnLine schema:
    - return_transaction_id: references parent ReturnTransactionDAO
    - product_type_id: references ProductType that was returned
    - quantity: number of units returned
    """
    __tablename__ = "return_productType_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    return_transaction_id = Column(Integer, ForeignKey("return_transactions.return_transaction_id", ondelete="CASCADE"), nullable=False)
    product_type_id = Column(Integer, ForeignKey("product_types.product_type_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relationship back to parent return
    return_obj: Mapped["ReturnTransactionDAO"] = relationship(
        "ReturnTransactionDAO",
        back_populates="product_lines"
    )

    product_type: Mapped["ProductTypeDAO"] = relationship(
        "ProductTypeDAO",
        back_populates="return_lines"
    )