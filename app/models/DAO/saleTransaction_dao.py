from sqlalchemy import Column, Integer, Enum, ForeignKey, Float
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from app.models.DAO.return_sale_association import return_sale_association
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .returnTranscation_dao import ReturnTransactionDAO
    from .loyaltyCard_dao import LoyaltyCard
    from .credit_dao import CreditDAO

class SaleTransactionDAO(Base):
    __tablename__ = "sale_transactions"

    id = Column(Integer, name='sale_transaction_id', primary_key=True, autoincrement=True)
    cost = Column(Float, nullable=False)
    paymentType = Column(Enum("CASH", "CREDIT_CARD", name="payment_types"), nullable=False)
    discountRate = Column(Float, nullable=False, default=0)

    loyalty_card_id = Column(Integer, ForeignKey("loyalty_card.id"))
    loyaltyCard: Mapped["LoyaltyCard"] = relationship("LoyaltyCard", backref="sale_transactions", uselist=False)

    returns: Mapped[List["ReturnTransactionDAO"]] = relationship(
        "ReturnTransactionDAO",
        secondary=return_sale_association,
        back_populates="sales"
    )
    
    credits: Mapped[List["CreditDAO"]] = relationship("CreditDAO", back_populates="sale_transaction")