import pytest
from app.controllers.accounting_controller import AccountingController
from tests.unit.fakes.fake_accounting_repo import FakeAccountingRepository

@pytest.mark.asyncio
async def test_get_balance_returns_value():
    repo = FakeAccountingRepository()
    repo.balance = 100.0
    controller = AccountingController(repo)

    balance = await controller.get_balance()
    assert balance == 100.0


@pytest.mark.asyncio
async def test_set_balance_updates_value():
    repo = FakeAccountingRepository()

    controller = AccountingController(repo)

    await controller.set_balance(250.0)

    balance = await controller.get_balance()
    assert balance == 250.0


@pytest.mark.asyncio
async def test_reset_balance_sets_zero():
    repo = FakeAccountingRepository()
    controller = AccountingController(repo)

    await controller.set_balance(300.0)
    await controller.reset_balance()

    balance = await controller.get_balance()
    assert balance == 0.0
