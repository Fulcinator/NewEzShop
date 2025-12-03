from sqlalchemy import Table, Column, Integer, ForeignKey, String
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .productType_dao import ProductTypeDAO
    from .debit_dao import DebitDAO

class OrderDAO(Base):
    __tablename__ = "orders"

    id = Column(Integer, name='order_id', primary_key=True, autoincrement=True)
    supplier = Column(String, nullable=False)
    status = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Integer, nullable=False)

    product_types: Mapped[List["ProductTypeDAO"]] = relationship(
        "ProductTypeDAO",
        secondary="order_productType_association",
        back_populates="orders"
    )
    
    debits: Mapped[List["DebitDAO"]] = relationship("DebitDAO", back_populates="order")