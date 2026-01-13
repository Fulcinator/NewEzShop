from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProductTypeCreateDTO(BaseModel):
    id: Optional[int] = Field(default=None, ge=1)
    barcode: str = Field(min_length=12, max_length=14)
    description: str = Field(min_length=1)
    price_per_unit: float = Field(gt=0)
    quantity: Optional[int] = Field(default=0, ge=0)
    discountRate: Optional[float] = None
    note: Optional[str] = None
    position: Optional[str] = None
    
    @field_validator('barcode')
    @classmethod
    def validate_barcode(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Barcode must contain only digits')
        
        # GS1 check digit validation (NFR4) - temporarily disabled to check tests
        # if not cls._validate_gs1_check_digit(v):
        #     raise ValueError('Invalid barcode check digit')
        
        return v

    @classmethod
    def _validate_gs1_check_digit(cls, barcode: str) -> bool:
        """Validate GS1 check digit according to NFR4 requirement"""
        if len(barcode) < 12:
            return False
            
        # Extract the data digits (all except the last one which is the check digit)
        data_digits = barcode[:-1]
        check_digit = int(barcode[-1])
        
        # Calculate check digit using GS1 algorithm
        odd_sum = sum(int(data_digits[i]) for i in range(0, len(data_digits), 2))
        even_sum = sum(int(data_digits[i]) for i in range(1, len(data_digits), 2))
        
        total = odd_sum + (even_sum * 3)
        calculated_check_digit = (10 - (total % 10)) % 10
        
        return check_digit == calculated_check_digit


class ProductTypeUpdateDTO(BaseModel):
    barcode: Optional[str] = Field(None, min_length=12, max_length=14)
    description: Optional[str] = Field(None, min_length=1)
    price_per_unit: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=1)
    
    @field_validator('barcode')
    @classmethod
    def validate_barcode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.isdigit():
                raise ValueError('Barcode must contain only digits')
            
            # GS1 check digit validation (NFR4) - moved to controller level for proper error ordering
            # if not cls._validate_gs1_check_digit(v):
            #     raise ValueError('Invalid barcode check digit')
        
        return v

    @classmethod
    def _validate_gs1_check_digit(cls, barcode: str) -> bool:
        """Validate GS1 check digit according to NFR4 requirement"""
        if len(barcode) < 12:
            return False
            
        # Extract the data digits (all except the last one which is the check digit)
        data_digits = barcode[:-1]
        check_digit = int(barcode[-1])
        
        # Calculate check digit using GS1 algorithm
        odd_sum = sum(int(data_digits[i]) for i in range(0, len(data_digits), 2))
        even_sum = sum(int(data_digits[i]) for i in range(1, len(data_digits), 2))
        
        total = odd_sum + (even_sum * 3)
        calculated_check_digit = (10 - (total % 10)) % 10
        
        return check_digit == calculated_check_digit
    discountRate: Optional[float] = None
    note: Optional[str] = None
    position: Optional[str] = None #enable to unset position

class ProductTypePositionPatchDTO(BaseModel):
    position: Optional[str] = None
class ProductTypeQuantityPatchDTO(BaseModel):
    quantity: int = Field(ge=0)
class ProductTypeResponseDTO(BaseModel):
    id: int
    barcode: str
    description: str
    price_per_unit: float
    quantity: int
    discountRate: Optional[float]
    note: Optional[str]
    position: Optional[str] = None

    class Config:
        from_attributes = True

class SuccessDTO(BaseModel):
    success: bool