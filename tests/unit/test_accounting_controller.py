import pytest
from unittest.mock import AsyncMock, MagicMock
from app.controllers.accounting_controller import AccountingController

@pytest.mark.asyncio
async def test_get_balance_returns_value():
    mock_repo = MagicMock()

    mock_repo.get_balance = AsyncMock(return_value=500.75)
    
    controller = AccountingController(repo=mock_repo)
    
    result = await controller.get_balance()
    
    assert result == 500.75
    mock_repo.get_balance.assert_awaited_once()

@pytest.mark.asyncio
async def test_set_balance_updates_value():
    
    mock_repo = MagicMock()
    mock_repo.set_balance = AsyncMock(return_value=None)
    
    controller = AccountingController(repo=mock_repo)
    
    await controller.set_balance(1000.0)
    
    mock_repo.set_balance.assert_awaited_once_with(1000.0)

@pytest.mark.asyncio
async def test_reset_balance_sets_zero():

    mock_repo = MagicMock()
    mock_repo.reset_balance = AsyncMock(return_value=None)
    
    controller = AccountingController(repo=mock_repo)
    
    await controller.reset_balance()
    
    mock_repo.reset_balance.assert_awaited_once()