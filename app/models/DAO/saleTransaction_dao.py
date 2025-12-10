from sqlalchemy import Column, Integer, Enum, ForeignKey, Float, DateTime
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

if TYPE_CHECKING:
    from .returnTransaction_dao import ReturnTransactionDAO
    from .loyaltyCard_dao import LoyaltyCard
    from .credit_dao import CreditDAO
    from .sale_product_association import SaleProductAssociation

class SaleTransactionDAO(Base):
    __tablename__ = "sale_transactions"

    id = Column(Integer, name='sale_transaction_id', primary_key=True, autoincrement=True)
    status = Column(Enum("OPEN", "PENDING", "PAID", name="sale_status"), nullable=False, default="OPEN")
    cost = Column(Float, nullable=False, default=0.0)
    paymentType = Column(Enum("CASH", "CREDIT_CARD", name="payment_types"), nullable=True)
    discountRate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    loyalty_card_id = Column(Integer, ForeignKey("loyalty_card.id"), nullable=True)
    loyaltyCard: Mapped[Optional["LoyaltyCard"]] = relationship("LoyaltyCard", backref="sale_transactions", uselist=False)

    # 1-N relationship with sale line items
    lines: Mapped[List["SaleProductAssociation"]] = relationship(
        "SaleProductAssociation",
        back_populates="sale",
        cascade="all, delete-orphan"
    )
    
    credits: Mapped[List["CreditDAO"]] = relationship("CreditDAO", back_populates="sale_transaction")