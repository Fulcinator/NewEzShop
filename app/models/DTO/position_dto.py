from pydantic import BaseModel, Field

class PositionDTO(BaseModel):
    aisleID: int = Field(ge=0)
    rackID: int = Field(ge=0)
    levelID: int = Field(ge=0)
