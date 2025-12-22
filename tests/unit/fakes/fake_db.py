class FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class FakeDB:
    def __init__(self, product=None, system_info=None):
        self.product = product
        self.system_info = system_info

    def query(self, model):
        if model.__name__ == "SaleTransactionDAO":
            return FakeQuery(self.sale)
        if model.__name__ == "ProductTypeDAO":
            return FakeQuery(self.product)
        if model.__name__ == "SystemInfoDAO":
            return FakeQuery(self.system_info)
        return FakeQuery(None)

    def commit(self):
        pass

    def refresh(self, obj):
        pass
