from app.repositories.accounting_repository import AccountingRepository

class AccountingController:
    def __init__(self, repo: AccountingRepository | None = None): # Allow dependency injection for testing
        self.repo = repo or AccountingRepository()

    async def get_balance(self) -> float:
        return self.repo.get_balance()

    async def reset_balance(self) -> None:
        self.repo.reset_balance()

    async def set_balance(self, amount: float) -> None:
        self.repo.set_balance(amount)
