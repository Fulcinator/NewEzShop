from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.DTO.return_product_association_dto import ReturnProductAssociationDTO


class ReturnTransactionDTO(BaseModel):
    id: int
    sale_id: int
    status: str  # OPEN, CLOSED, REIMBURSED
    created_at: datetime
    closed_at: Optional[datetime] = None
    lines: List[ReturnProductAssociationDTO] = []

    class Config:
        from_attributes = True