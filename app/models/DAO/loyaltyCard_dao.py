from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import Optional
class LoyaltyCardDAO(Base):
    __tablename__ = "loyalty_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String(10), unique=True, nullable=False)
    points = Column(Integer, nullable=False, default=0)

    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), unique=True, nullable=True)

    customer: Mapped[Optional["CustomerDAO"]] = relationship(
        "CustomerDAO", back_populates="loyalty_card", lazy="selectin"
    )
