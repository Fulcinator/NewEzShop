from sqlalchemy import Table, Column, Integer, String, Float, Enum, DateTime, func
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List
from app.models.order_status import OrderStatus
from app.models.DAO.order_productType_association import order_productType_association

class OrderDAO(Base):
    __tablename__ = "orders"

    id = Column(Integer, name='order_id', primary_key=True, autoincrement=True)
    supplier = Column(String, nullable=True)  # Can be null for reorder warnings
    status = Column(Enum(OrderStatus), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)

    issue_date = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    product_types: Mapped[List["ProductTypeDAO"]] = relationship(
        "ProductTypeDAO",
        secondary=order_productType_association,
        back_populates="orders"
    )

    debits: Mapped[List["DebitDAO"]] = relationship("DebitDAO", back_populates="order")