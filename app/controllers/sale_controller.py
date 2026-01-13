from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.sale_repository import SaleRepository
from app.services.mapper_service import saleTransactionDao_toDto
from app.models.DTO.saleTransaction_dto import SaleTransactionDTO
from app.models.DTO.sale_product_association_dto import SaleProductAssociationDTO
from app.models.DAO.productType_dao import ProductTypeDAO
from app.models.DAO.system_dao import SystemInfoDAO


class SaleController:
    def __init__(self, db: AsyncSession):
        self.repo = SaleRepository(db)

    async def start_sale(self) -> SaleTransactionDTO:
        sale_data = {
            "status": "OPEN",
            "discountRate": 0.0,
            "cost": 0.0
        }
        dao = await self.repo.create_sale(sale_data)
        return saleTransactionDao_toDto(dao, SaleTransactionDTO, include_lines=False)

    async def get_all_sales(self) -> List[SaleTransactionDTO]:
        daos = await self.repo.get_all_sales()
        return [saleTransactionDao_toDto(d, SaleTransactionDTO, include_lines=True) for d in daos]
    async def get_sale(self, sale_id: int) -> Optional[SaleTransactionDTO]:
        dao = await self.repo.get_sale_by_id(sale_id)
        if dao:
            return saleTransactionDao_toDto(dao, SaleTransactionDTO, include_lines=True)
        return None

    async def delete_sale(self, sale_id: int) -> bool:
        return await self.repo.delete_sale(sale_id)

    async def add_product_to_sale(self, sale_id: int, barcode: str, amount: int):
        return await self.repo.add_product_to_sale(sale_id, barcode, amount)

    async def remove_product_from_sale(self, sale_id: int, barcode: str, amount: int):
        return await self.repo.remove_product_from_sale(sale_id, barcode, amount)

    async def apply_discount_to_sale(self, sale_id: int, discount_rate: float):
        return await self.repo.apply_discount_to_sale(sale_id, discount_rate)
    
    async def apply_discount_to_product(self, sale_id: int, product_barcode: str, discount_rate: float):
        return await self.repo.apply_discount_to_product(sale_id, product_barcode, discount_rate)

    async def close_sale(self, sale_id: int):
        return await self.repo.close_sale(sale_id)

    async def pay_sale(self, sale_id: int, cash_amount: float):
        return await self.repo.pay_sale(sale_id, cash_amount)
    
    async def compute_points(self, sale_id: int):
        return await self.repo.compute_points(sale_id)