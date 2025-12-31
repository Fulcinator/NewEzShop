from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from app.models.DAO.balanceOperation_dao import BalanceOperationDAO
from typing import Optional
class DebitDAO(BalanceOperationDAO):
    __tablename__ = "debits"

    id = Column(Integer, ForeignKey('balance_operations.balance_operation_id'), name='debit_id', primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=True)
    return_transaction_id = Column(Integer, ForeignKey("return_transactions.return_transaction_id"), nullable=True)

    order: Mapped[Optional["OrderDAO"]] = relationship("OrderDAO", back_populates="debits")
    return_transaction: Mapped[Optional["ReturnTransactionDAO"]] = relationship("ReturnTransactionDAO", back_populates="debits")

    __mapper_args__ = {
        "polymorphic_identity": "debit",
    }