import pytest
from unittest.mock import MagicMock, patch
from app.controllers.sale_controller import SaleController
from app.models.DTO.saleTransaction_dto import SaleTransactionDTO

class FakeSale:
    def __init__(self, status="OPEN", discount_rate=0.0):
        self.id = 1
        self.status = status
        self.discount_rate = discount_rate
        self.sale_lines = []


class FakeProduct:
    def __init__(self, quantity=10, sellPrice=5.0):
        self.id = 100
        self.barcode = "ABC"
        self.quantity = quantity
        self.sellPrice = sellPrice


class FakeLine:
    def __init__(self, product_id, quantity, unit_price, discount_rate=0.0):
        self.id = 1
        self.product_type_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.discount_rate = discount_rate


class FakeSystemInfo:
    def __init__(self, balance=0.0):
        self.balance = balance

@pytest.fixture
def repo():
    repo = MagicMock()
    repo.db = MagicMock()
    return repo


@pytest.fixture
def controller(repo):
    with patch("app.controllers.sale_controller.SaleRepository", return_value=repo):
        yield SaleController(db=MagicMock())


def test_start_sale(controller, repo):
    dao = MagicMock()
    repo.create_sale.return_value = dao

    with patch(
        "app.controllers.sale_controller.saleTransactionDao_toDto",
        return_value=SaleTransactionDTO(
            sale_transaction_id=1,
            status="OPEN",
            cost=0.0,
            discountRate=0.0,
            created_at="2024-01-01T00:00:00",
            lines=[]
        )
    ):
        result = controller.start_sale()

    repo.create_sale.assert_called_once()
    assert result.status == "OPEN"


def test_get_sale_found(controller, repo):
    repo.get_sale_by_id.return_value = MagicMock()

    with patch(
        "app.controllers.sale_controller.saleTransactionDao_toDto",
        return_value="DTO"
    ):
        assert controller.get_sale(1) == "DTO"


def test_get_sale_not_found(controller, repo):
    repo.get_sale_by_id.return_value = None
    assert controller.get_sale(1) is None



def test_delete_sale_open(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    repo.delete_sale.return_value = True

    assert controller.delete_sale(1) is True


def test_delete_sale_paid(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="PAID")
    assert controller.delete_sale(1) is False



def test_add_product_success(controller, repo):
    sale = FakeSale(status="OPEN")
    product = FakeProduct(quantity=10)

    repo.get_sale_by_id.return_value = sale
    repo.db.query().filter().first.return_value = product

    assert controller.add_product_to_sale(1, "ABC", 2) is True
    assert product.quantity == 8


def test_add_product_insufficient_quantity(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    repo.db.query().filter().first.return_value = FakeProduct(quantity=1)

    assert controller.add_product_to_sale(1, "ABC", 5) is False


def test_add_product_sale_closed(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="PAID")
    assert controller.add_product_to_sale(1, "ABC", 1) is False



def test_remove_product_partial(controller, repo):
    sale = FakeSale(status="OPEN")
    product = FakeProduct(quantity=5)
    line = FakeLine(product.id, quantity=3, unit_price=5)

    repo.get_sale_by_id.return_value = sale
    repo.db.query().filter().first.return_value = product
    repo.get_line_items.return_value = [line]

    assert controller.remove_product_from_sale(1, "ABC", 1) is True
    assert line.quantity == 2
    assert product.quantity == 6


def test_remove_product_not_found(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale()
    repo.db.query().filter().first.return_value = None

    assert controller.remove_product_from_sale(1, "ABC", 1) is False


def test_apply_discount_valid(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    assert controller.apply_discount_to_sale(1, 0.2) is True


def test_apply_discount_invalid(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    assert controller.apply_discount_to_sale(1, 1.5) is False



def test_close_sale_success(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    assert controller.close_sale(1) is True


def test_close_sale_invalid_state(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="PAID")
    assert controller.close_sale(1) is False


def test_pay_sale_success(controller, repo):
    sale = FakeSale(status="PENDING")
    line = FakeLine(1, 2, 10, 0.1)
    sale.sale_lines = [line]

    system = FakeSystemInfo(balance=100)

    repo.get_sale_by_id.return_value = sale
    repo.pay_sale.return_value = (sale, 5.0)
    repo.db.query().first.return_value = system

    result = controller.pay_sale(1, 50)

    assert result == {"change": 5.0}
    assert system.balance > 100


def test_pay_sale_wrong_state(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")
    assert controller.pay_sale(1, 10) is None



def test_compute_points_success(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale()
    repo.compute_points.return_value = 50

    assert controller.compute_points(1) == {"points": 50}


def test_compute_points_sale_not_found(controller, repo):
    repo.get_sale_by_id.return_value = None
    assert controller.compute_points(1) is None

def test_apply_discount_to_product_success(controller, repo):
    sale = FakeSale(status="OPEN")
    product = FakeProduct(quantity=10)
    line = FakeLine(product.id, quantity=2, unit_price=10)

    repo.get_sale_by_id.return_value = sale
    repo.db.query().filter().first.return_value = product
    repo.get_line_items.return_value = [line]

    result = controller.apply_discount_to_product(
        sale_id=1,
        product_barcode="ABC",
        discount_rate=0.3
    )

    assert result is True
    assert line.discount_rate == 0.3


def test_apply_discount_to_product_invalid_discount(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")

    result = controller.apply_discount_to_product(
        sale_id=1,
        product_barcode="ABC",
        discount_rate=1.5
    )

    assert result is False

def test_add_product_invalid_amount(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="OPEN")

    result = controller.add_product_to_sale(1, "ABC", 0)

    assert result is False


def test_remove_product_sale_not_open(controller, repo):
    repo.get_sale_by_id.return_value = FakeSale(status="PAID")

    result = controller.remove_product_from_sale(1, "ABC", 1)

    assert result is False

def test_remove_product_line_not_found(controller, repo):
    sale = FakeSale(status="OPEN")
    product = FakeProduct(quantity=5)

    repo.get_sale_by_id.return_value = sale
    repo.db.query().filter().first.return_value = product
    repo.get_line_items.return_value = [
        FakeLine(product_id=999, quantity=1, unit_price=5)
    ]

    result = controller.remove_product_from_sale(1, "ABC", 1)

    assert result is False
