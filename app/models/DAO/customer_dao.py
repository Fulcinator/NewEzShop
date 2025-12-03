from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .loyaltyCard_dao import LoyaltyCard

class CustomerDAO(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    loyaltyCard: Mapped["LoyaltyCard"] = relationship("LoyaltyCard", back_populates="customer", uselist=False)