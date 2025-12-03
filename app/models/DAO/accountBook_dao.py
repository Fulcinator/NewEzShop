from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .shop_dao import ShopDAO
    from .balanceOperation_dao import BalanceOperationDAO

class AccountBookDAO(Base):
    __tablename__ = "account_books"

    id = Column(Integer, name='account_book_id', primary_key=True, autoincrement=True)
    shop_id = Column(ForeignKey('shops.shop_id'), nullable=False)
    shop: Mapped["ShopDAO"] = relationship(back_populates="account_book")

    balance_operations: Mapped[List["BalanceOperationDAO"]] = relationship(back_populates="account_book")
    