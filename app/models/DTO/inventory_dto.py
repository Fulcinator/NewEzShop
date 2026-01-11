from pydantic import BaseModel, Field

class QuantityUpdateDTO(BaseModel):
    new_quantity: int = Field(ge=0)
