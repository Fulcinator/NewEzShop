from app.repositories.inventory_repository import InventoryRepository
from app.models.DTO.inventory_dto import QuantityUpdateDTO
from app.models.DTO.position_dto import PositionDTO
from app.models.DTO.product_type_dto import ProductTypeResponseDTO
from app.services.mapper_service import simple_map


class InventoryController:
    def __init__(self):
        self.repo = InventoryRepository()

    async def update_quantity(self, product_type_id: int, dto: QuantityUpdateDTO) -> ProductTypeResponseDTO:
        pt = await self.repo.update_quantity(product_type_id, dto.new_quantity)
        return simple_map(pt, ProductTypeResponseDTO)

    async def update_position(self, product_type_id: int, dto: PositionDTO) -> ProductTypeResponseDTO:
        pt = await self.repo.update_position(
            product_type_id,
            dto.aisleID,
            dto.rackID,
            dto.levelID
        )
        return simple_map(pt, ProductTypeResponseDTO)
