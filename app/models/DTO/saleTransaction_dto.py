from pydantic import BaseModel, Field,ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.DTO.sale_product_association_dto import SaleProductAssociationDTO


class SaleTransactionDTO(BaseModel):
    id: int = Field(alias="sale_transaction_id", default=None)
    status: str  # OPEN, PENDING, PAID
    cost: float
    payment_type: Optional[str] = None  # CASH, CREDIT_CARD
    discount_rate: float = 0.0
    created_at: datetime
    closed_at: Optional[datetime] = None
    loyalty_card_id: Optional[int] = None
    lines: List[SaleProductAssociationDTO] = []

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Allows mapping from DAO 'id' to DTO 'sale_transaction_id'
    )