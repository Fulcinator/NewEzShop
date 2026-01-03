from typing import List, Optional
from app.repositories.product_type_repository import ProductTypeRepository
from app.services.mapper_service import ProductTypeDao_toDto
from app.models.DTO.product_type_dto import (
    ProductTypeCreateDTO,
    ProductTypePositionPatchDTO,
    ProductTypeQuantityPatchDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO,
    SuccessDTO,
)


class ProductTypeController:
    def __init__(self):
        self.repo = ProductTypeRepository()

    async def create(self, dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        dao = await self.repo.create_product_type(dto)
        return ProductTypeDao_toDto(dao, ProductTypeResponseDTO)

    async def get_by_id(self, id: int) -> ProductTypeResponseDTO:
        dao = await self.repo.get_product_type_by_id(id)
        return ProductTypeDao_toDto(dao, ProductTypeResponseDTO)
    
    async def update(self, id: int, dto: ProductTypeUpdateDTO) -> ProductTypeResponseDTO:
        dao = await self.repo.update_product_type(id, dto)
        return ProductTypeDao_toDto(dao, ProductTypeResponseDTO)

    async def delete(self, id: int):
        return await self.repo.delete_product_type(id)

    async def list_all(self) -> List[ProductTypeResponseDTO]:
        daos = await self.repo.list_product_types()
        return [ProductTypeDao_toDto(d, ProductTypeResponseDTO) for d in daos]

    async def get_by_barcode(self, barcode: str) -> ProductTypeResponseDTO:
        dao = await self.repo.get_product_type_by_barcode(barcode)
        return ProductTypeDao_toDto(dao, ProductTypeResponseDTO)
    
    async def search(self, description: Optional[str] = None) -> List[ProductTypeResponseDTO]:
        daos = await self.repo.search_product_types(description=description)
        return [ProductTypeDao_toDto(d, ProductTypeResponseDTO) for d in daos]

    async def patch_position(self, id: int, dto: ProductTypePositionPatchDTO) -> SuccessDTO:
        await self.repo.patch_position(id, dto.position)
        return SuccessDTO(success=True)

    async def patch_quantity(self, id: int, dto: ProductTypeQuantityPatchDTO) -> SuccessDTO:
        await self.repo.patch_quantity(id, dto.quantity)
        return SuccessDTO(success=True)