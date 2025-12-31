from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List, Optional
from datetime import datetime
class ReturnTransactionDAO(Base):
    __tablename__ = "return_transactions"

    id = Column(Integer, name='return_transaction_id', primary_key=True, autoincrement=True)
    sale_transaction_id = Column(Integer, ForeignKey("sale_transactions.sale_transaction_id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("OPEN", "CLOSED", "REIMBURSED", name="return_status"), nullable=False, default="OPEN")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # N-1 relationship back to the original sale
    sale: Mapped[Optional["SaleTransactionDAO"]] = relationship(
        "SaleTransactionDAO",
        foreign_keys=[sale_transaction_id]
    )

    # 1-N relationship with returned product types (which products were returned)
    product_lines: Mapped[List["ReturnProductAssociation"]] = relationship(
        "ReturnProductAssociation",
        back_populates="return_obj",
        cascade="all, delete-orphan"
    )
    
    debits: Mapped[List["DebitDAO"]] = relationship("DebitDAO", back_populates="return_transaction")