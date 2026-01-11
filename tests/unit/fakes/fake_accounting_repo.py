class FakeAccountingRepository:
    def __init__(self):
        self.balance = 0.0

    def get_balance(self):
        return self.balance

    def set_balance(self, amount: float):
        self.balance = amount

    def reset_balance(self):
        self.balance = 0.0    
