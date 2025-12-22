class FakeSale:
    def __init__(self, status="OPEN", discountRate=0.0):
        self.id = 1
        self.status = status
        self.discountRate = discountRate
        self.cost = 100.0
        self.paymentType = 'CASH'
        self.created_at = '2024-01-01 00:00:00'
        self.closed_at = '2024-01-01 01:00:00'
        self.loyalty_card_id = 1
        self.sale_lines = []


class FakeLine:
    def __init__(self, product_type_id, quantity, unit_price, discount_rate=0.0):
        self.id = 1
        self.product_type_id = product_type_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_rate = discount_rate


class FakeSaleRepository:
    def __init__(self, db):
        self.db = db
        self.sale = None
        self.lines = []

    def create_sale(self, data):
        self.sale = FakeSale(status=data["status"])
        return self.sale

    def get_all_sales(self):
        return [self.sale] if self.sale else []

    def get_sale_by_id(self, sale_id):
        return self.sale

    def delete_sale(self, sale_id):
        self.sale = None
        return True

    def add_line_item(self, sale_id, data):
        line = FakeLine(
            product_type_id=data["product_type_id"],
            quantity=data["quantity"],
            unit_price=data["unit_price"]
        )
        self.lines.append(line)
        self.sale.sale_lines.append(line)

    def get_line_items(self, sale_id):
        return self.lines

    def remove_line_item(self, line_id):
        self.lines = []

    def apply_discount(self, sale_id, discount_rate):
        self.sale.discount_rate = discount_rate

    def close_sale(self, sale_id):
        self.sale.status = "PENDING"

    def pay_sale(self, sale_id, cash_amount):
        return self.sale, 5.0

    def compute_points(self, sale_id):
        return 10
