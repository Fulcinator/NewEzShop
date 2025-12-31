from sqlalchemy import Column, Integer
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import Optional

class PositionDAO(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aisleID = Column(Integer, nullable=False)
    rackID = Column(Integer, nullable=False)
    levelID = Column(Integer, nullable=False)

    product_type: Mapped[Optional["ProductTypeDAO"]] = relationship("ProductTypeDAO", back_populates="position")
