from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .accountBook_dao import AccountBookDAO

class BalanceOperationDAO(Base):
    __tablename__ = "balance_operations"

    id = Column(Integer, name='balance_operation_id', primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    date = Column(String, nullable=False)

    op_type = Column("type", String(50), nullable=False)

    account_book_id = Column(Integer, ForeignKey('account_books.account_book_id'), nullable=False)
    account_book: Mapped["AccountBookDAO"] = relationship("AccountBookDAO", back_populates="balance_operations")

    __mapper_args__ = {
        "polymorphic_on": op_type,
        "polymorphic_identity": "balance_operation",
    }


    