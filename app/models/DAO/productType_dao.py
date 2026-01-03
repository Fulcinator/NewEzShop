from sqlalchemy import Column, Integer, String, ForeignKey, Float
from app.database.database import Base
from typing import List, Optional
from sqlalchemy.orm import relationship, Mapped
from app.models.DAO.order_productType_association import order_productType_association
class ProductTypeDAO(Base):
    __tablename__ = "product_types"

    id = Column(Integer, name='product_type_id', primary_key=True, autoincrement=True)
    barcode = Column(String(14), unique=True, nullable=False)
    description = Column(String, nullable=True, unique=True) # description is the name of the product
    price_per_unit = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discountRate = Column(Float, nullable=True)
    note = Column(String, nullable=True)

    position_id = Column(Integer, ForeignKey("positions.id"), nullable=True)
    position: Mapped[Optional["PositionDAO"]] = relationship("PositionDAO", back_populates="product_type", cascade="all, delete-orphan", uselist=False, single_parent=True)

    orders: Mapped[List["OrderDAO"]] = relationship(
        "OrderDAO",
        secondary=order_productType_association,
        back_populates="product_types"
    )   

    shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=False)
    shop: Mapped["ShopDAO"] = relationship("ShopDAO", back_populates="product_types")

    products: Mapped[List["ProductDAO"]] = relationship("ProductDAO", back_populates="product_type", cascade="all, delete-orphan")

    return_lines: Mapped[List["ReturnProductAssociation"]] = relationship(
        "ReturnProductAssociation",
        back_populates="product_type"
    )