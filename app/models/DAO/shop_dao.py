from sqlalchemy import Column, Integer
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List

class ShopDAO(Base):
    __tablename__ = "shops"

    id = Column(Integer, name='shop_id', primary_key=True, autoincrement=True)
    product_types: Mapped[List["ProductTypeDAO"]] = relationship("ProductTypeDAO", back_populates="shop")

    account_book: Mapped["AccountBookDAO"] = relationship(back_populates="shop", uselist=False)
