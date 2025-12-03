from sqlalchemy import Column, Integer
from app.database.database import Base
from sqlalchemy.orm import relationship, Mapped
from app.models.DAO.return_sale_association import return_sale_association
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .saleTransaction_dao import SaleTransactionDAO
    from .productType_dao import ProductTypeDAO
    from .debit_dao import DebitDAO

class ReturnTransactionDAO(Base):
    __tablename__ = "return_transactions"

    id = Column(Integer, name='return_transaction_id', primary_key=True, autoincrement=True)
    quantity = Column(Integer, nullable=False)
    returnedValue = Column(Integer, nullable=False)

    sales: Mapped[List["SaleTransactionDAO"]] = relationship(
        "SaleTransactionDAO",
        secondary=return_sale_association,
        back_populates="returns"
    )

    product_types: Mapped[List["ProductTypeDAO"]] = relationship(
        "ProductTypeDAO",
        secondary="return_productType_association",
        back_populates="returns"
    )
    
    debits: Mapped[List["DebitDAO"]] = relationship("DebitDAO", back_populates="return_transaction")