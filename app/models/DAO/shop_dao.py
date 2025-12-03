from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .productType_dao import ProductTypeDAO
    from .accountBook_dao import AccountBookDAO

class ShopDAO(Base):
    __tablename__ = "shops"

    id = Column(Integer, name='shop_id', primary_key=True, autoincrement=True)
    product_types: Mapped[List["ProductTypeDAO"]] = relationship("ProductTypeDAO", back_populates="shop")

    account_book: Mapped["AccountBookDAO"] = relationship(back_populates="shop", uselist=False)
