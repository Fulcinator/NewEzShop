from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .customer_dao import CustomerDAO

class LoyaltyCard(Base):
    __tablename__ = "loyalty_card"

    id = Column(Integer, primary_key=True, autoincrement=True)
    points = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    customer: Mapped["CustomerDAO"] = relationship("CustomerDAO", back_populates="loyaltyCard")