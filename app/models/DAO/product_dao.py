from sqlalchemy import Column, Integer, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List

class ProductDAO(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_type_id = Column(Integer, ForeignKey("product_types.product_type_id"), nullable=False)

    product_type: Mapped["ProductTypeDAO"] = relationship(
        "ProductTypeDAO",
        back_populates="products"
    )
