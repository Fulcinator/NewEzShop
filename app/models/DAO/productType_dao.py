from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .position_dao import PositionDAO
    from .order_dao import OrderDAO
    from .shop_dao import ShopDAO
    from .returnTranscation_dao import ReturnTransactionDAO
    from .product_dao import ProductDAO

class ProductTypeDAO(Base):
    __tablename__ = "product_types"

    id = Column(Integer, name='product_type_id', primary_key=True, autoincrement=True)
    barcode = Column(String(14), unique=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    sellPrice = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discountRate = Column(Float, nullable=True)
    notes = Column(String, nullable=True)

    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    position: Mapped[Optional["PositionDAO"]] = relationship("PositionDAO", back_populates="product_type")

    orders: Mapped[List["OrderDAO"]] = relationship(
        "OrderDAO",
        secondary="order_productType_association",
        back_populates="product_types"
    )
    
    returns: Mapped[List["ReturnTransactionDAO"]] = relationship(
        "ReturnTransactionDAO",
        secondary="return_productType_association",
        back_populates="product_types"
    )

    shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=False)
    shop: Mapped["ShopDAO"] = relationship("ShopDAO", back_populates="product_types")

    products: Mapped[List["ProductDAO"]] = relationship("ProductDAO", back_populates="product_type")