from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO
from typing import Optional
class CreditDAO(BalanceOperationDAO):
    __tablename__ = "credits"

    id = Column(Integer, ForeignKey('balance_operations.balance_operation_id'), name='credit_id', primary_key=True)

    sale_transaction_id = Column(Integer, ForeignKey("sale_transactions.sale_transaction_id"), nullable=True)

    sale_transaction: Mapped[Optional["SaleTransactionDAO"]] = relationship("SaleTransactionDAO", back_populates="credits")

    __mapper_args__ = {
        "polymorphic_identity": "credit",
    }

