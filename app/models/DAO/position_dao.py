from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .productType_dao import ProductTypeDAO

class PositionDAO(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aisleID = Column(Integer, nullable=False)
    rackID = Column(Integer, nullable=False)
    levelID = Column(Integer, nullable=False)

    product_type: Mapped[Optional["ProductTypeDAO"]] = relationship("ProductTypeDAO", back_populates="position")
