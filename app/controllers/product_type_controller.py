from typing import List, Optional
from app.repositories.product_type_repository import ProductTypeRepository
from app.services.mapper_service import simple_map
from app.models.DTO.product_type_dto import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
    ProductTypeResponseDTO,
)


class ProductTypeController:
    def __init__(self):
        self.repo = ProductTypeRepository()

    async def create(self, dto: ProductTypeCreateDTO) -> ProductTypeResponseDTO:
        dao = await self.repo.create_product_type(dto)
        return simple_map(dao, ProductTypeResponseDTO)

    async def update(self, id: int, dto: ProductTypeUpdateDTO) -> ProductTypeResponseDTO:
        dao = await self.repo.update_product_type(id, dto)
        return simple_map(dao, ProductTypeResponseDTO)

    async def delete(self, id: int):
        return await self.repo.delete_product_type(id)

    async def list_all(self) -> List[ProductTypeResponseDTO]:
        daos = await self.repo.list_product_types()
        return [simple_map(d, ProductTypeResponseDTO) for d in daos]

    async def search(self, barcode: Optional[str] = None, description: Optional[str] = None) -> List[ProductTypeResponseDTO]:
        daos = await self.repo.search_product_types(barcode, description)
        return [simple_map(d, ProductTypeResponseDTO) for d in daos]

