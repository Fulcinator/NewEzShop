from sqlalchemy import Column, Integer, String
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .loyaltyCard_dao import LoyaltyCardDAO

class CustomerDAO(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    loyalty_card: Mapped[Optional["LoyaltyCardDAO"]] = relationship(
    "LoyaltyCardDAO", back_populates="customer", uselist=False
)
