class FakeReturn:
    def __init__(self, sale_transaction_id=1, status="OPEN"):
        self.id = 1
        self.sale_transaction_id = sale_transaction_id
        self.status = status
        self.created_at = "2024-01-01 00:00:00"
        self.closed_at = '2024-01-01 01:00:00'
        self.returned_products = []


class FakeReturnedProduct:
    _id = 1

    def __init__(self, product_type_id, quantity):
        self.id = FakeReturnedProduct._id
        FakeReturnedProduct._id += 1

        self.product_type_id = product_type_id
        self.quantity = quantity


class FakeReturnRepository:
    def __init__(self, db):
        self.db = db
        self.return_obj = None

    def create_return(self, data):
        self.return_obj = FakeReturn(
            sale_transaction_id=data["sale_transaction_id"],
            status=data["status"]
        )
        return self.return_obj

    def get_all_returns(self):
        return [self.return_obj] if self.return_obj else []

    def get_return_by_id(self, return_id):
        return self.return_obj if self.return_obj and self.return_obj.id == return_id else None

    def get_returns_by_sale_id(self, sale_id):
        if self.return_obj and self.return_obj.sale_transaction_id == sale_id:
            return [self.return_obj]
        return []

    def delete_return(self, return_id):
        self.return_obj = None
        return True

    def add_returned_product(self, return_id, data):
        rp = FakeReturnedProduct(
            product_type_id=data["product_type_id"],
            quantity=data["quantity"]
        )
        self.return_obj.returned_products.append(rp)

    def get_returned_products(self, return_id):
        return self.return_obj.returned_products

    def remove_returned_product(self, rp_id):
        self.return_obj.returned_products = [
            rp for rp in self.return_obj.returned_products if rp.id != rp_id
        ]

    def close_return(self, return_id):
        self.return_obj.status = "CLOSED"

    def mark_reimbursed(self, return_id):
        self.return_obj.status = "REIMBURSED"