class FakeCustomer:
    def __init__(self, id=1, name="Mario", surname="Rossi"):
        self.id = id
        self.name = name
        self.surname = surname
        self.loyalty_card_id = None


class FakeCustomerRepository:
    def __init__(self):
        self.customers = {}
        self.next_id = 1

    async def create_customer(self, dto):
        customer = FakeCustomer(
            id=self.next_id,
            name=dto.name,
            surname=dto.surname
        )
        self.customers[self.next_id] = customer
        self.next_id += 1
        return customer

    async def get_customer_by_id(self, customer_id):
        return self.customers.get(customer_id)

    async def list_customers(self):
        return list(self.customers.values())

    async def search_customers(self, name=None, surname=None):
        return [
            c for c in self.customers.values()
            if (name is None or c.name == name)
            and (surname is None or c.surname == surname)
        ]

    async def update_customer(self, customer_id, dto):
        customer = self.customers.get(customer_id)
        if not customer:
            return None
        customer.name = dto.name or customer.name
        customer.surname = dto.surname or customer.surname
        return customer

    async def delete_customer(self, customer_id):
        self.customers.pop(customer_id, None)