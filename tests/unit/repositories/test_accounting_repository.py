import pytest
from app.repositories.accounting_repository import AccountingRepository
from app.models.errors.balance_error import BalanceError
from app.models.DAO.system_dao import SystemInfoDAO
from sqlalchemy import select, delete

@pytest.mark.asyncio
class TestAccountingRepository:

    async def test_get_balance_initializes_to_zero(self, db_session):
        """Tests that if no info exists, it creates it with 0.0 balance."""
        # Clear any existing system info from integration tests
        await db_session.execute(delete(SystemInfoDAO))
        await db_session.commit()
        
        repo = AccountingRepository()
        
        balance = await repo.get_balance()
        
        assert balance == 0.0
        # Verify it actually created a row in the DB
        result = await db_session.execute(select(SystemInfoDAO))
        assert len(result.scalars().all()) == 1

    async def test_set_balance_success(self, db_session):
        repo = AccountingRepository()
        
        await repo.set_balance(500.50)
        
        balance = await repo.get_balance()
        assert balance == 500.50

    async def test_set_balance_negative_raises_error(self, db_session):
        repo = AccountingRepository()
        
        with pytest.raises(BalanceError, match="Balance cannot be negative"):
            await repo.set_balance(-100.0)

    async def test_reset_balance(self, db_session):
        repo = AccountingRepository()
        
        # Set to something first
        await repo.set_balance(1000.0)
        # Reset
        await repo.reset_balance()
        
        balance = await repo.get_balance()
        assert balance == 0.0