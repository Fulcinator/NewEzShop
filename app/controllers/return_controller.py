from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.return_repository import ReturnRepository
from app.services.mapper_service import ReturnTransactionDao_toDto
from app.models.DTO.returnTransaction_dto import ReturnTransactionDTO


class ReturnController:
    def __init__(self, db: AsyncSession):
        self.repo = ReturnRepository(db)

    async def start_return(self, sale_id: int) -> ReturnTransactionDTO:
        dao = await self.repo.create_return(sale_id)
        return ReturnTransactionDao_toDto(dao, ReturnTransactionDTO)

    async def get_all_returns(self) -> List[ReturnTransactionDTO]:
        daos = await self.repo.get_all_returns()
        return [ReturnTransactionDao_toDto(d, ReturnTransactionDTO) for d in daos]

    async def get_return(self, return_id: int) -> Optional[ReturnTransactionDTO]:
        dao = await self.repo.get_return_by_id(return_id)
        return ReturnTransactionDao_toDto(dao, ReturnTransactionDTO)

    async def get_returns_by_sale(self, sale_id: int) -> List[ReturnTransactionDTO]:
        daos = await self.repo.get_returns_by_sale_id(sale_id)
        return [ReturnTransactionDao_toDto(d, ReturnTransactionDTO) for d in daos]

    async def delete_return(self, return_id: int) -> bool:
        return await self.repo.delete_return(return_id)

    async def add_product_to_return(self, return_id: int, barcode: str, amount: int):
        await self.repo.add_product_to_return(return_id, barcode, amount)

    async def remove_product_from_return(self, return_id: int, barcode: str, amount: int):
        await self.repo.remove_product_from_return(return_id, barcode, amount)

    async def close_return(self, return_id: int):
        await self.repo.close_return(return_id)

    async def reimburse_return(self, return_id: int) -> dict:
        return await self.repo.reimburse_return(return_id)