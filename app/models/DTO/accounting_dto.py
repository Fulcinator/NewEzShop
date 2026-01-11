from pydantic import BaseModel

class BalanceResponseDTO(BaseModel):
    balance: float
