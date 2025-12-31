from sqlalchemy import Column, Integer, Enum, ForeignKey, Float, DateTime
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List, Optional
from datetime import datetime
class SaleTransactionDAO(Base):
    __tablename__ = "sale_transactions"

    id = Column(Integer, name='sale_transaction_id', primary_key=True, autoincrement=True)
    status = Column(Enum("OPEN", "PENDING", "PAID", name="sale_status"), nullable=False, default="OPEN")
    cost = Column(Float, nullable=False, default=0.0)
    paymentType = Column(Enum("CASH", "CREDIT_CARD", name="payment_types"), nullable=True)
    discountRate = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    loyalty_card_id = Column(Integer, ForeignKey("loyalty_cards.id"), nullable=True)
    loyaltyCard: Mapped[Optional["LoyaltyCardDAO"]] = relationship("LoyaltyCardDAO", backref="sale_transactions", uselist=False)

    # 1-N relationship with sale line items
    lines: Mapped[List["SaleProductAssociation"]] = relationship(
        "SaleProductAssociation",
        back_populates="sale",
        cascade="all, delete-orphan"
    )
    
    credits: Mapped[List["CreditDAO"]] = relationship("CreditDAO", back_populates="sale_transaction")