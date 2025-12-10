from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import AsyncSessionLocal
from app.models.DAO.system_dao import SystemInfoDAO
from app.models.errors.balance_error import BalanceError

class AccountingRepository:
    async def get_balance(self) -> float:
        async with AsyncSessionLocal() as session:
            system_info = await self._get_or_create_system_info(session)
            return system_info.balance

    async def reset_balance(self) -> None:
        async with AsyncSessionLocal() as session:
            system_info = await self._get_or_create_system_info(session)
            system_info.balance = 0.0
            await session.commit()

    async def set_balance(self, amount: float) -> None:
        if amount < 0:
            raise BalanceError("Balance cannot be negative")
        async with AsyncSessionLocal() as session:
            system_info = await self._get_or_create_system_info(session)
            system_info.balance = amount
            await session.commit()

    async def _get_or_create_system_info(self, session: AsyncSession) -> SystemInfoDAO:
        result = await session.execute(
            SystemInfoDAO.__table__.select()
        )
        row = result.first()
        if row:
            system_info = await session.get(SystemInfoDAO, row[0])
        else:
            system_info = SystemInfoDAO(balance=0.0)
            session.add(system_info)
            await session.commit()
            await session.refresh(system_info)
        return system_info
