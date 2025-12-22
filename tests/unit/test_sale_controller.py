from app.controllers.sale_controller import SaleController
from tests.unit.fakes.fake_sale_repo import FakeSaleRepository, FakeSale
from tests.unit.fakes.fake_db import FakeDB

def test_start_sale_creates_open_sale():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    controller.repo = FakeSaleRepository(fake_db)

    sale = controller.start_sale()

    assert sale is not None

def test_delete_sale_open_success():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale(status="OPEN")
    controller.repo = repo

    result = controller.delete_sale(1)

    assert result is True


def test_delete_sale_paid_fails():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale(status="PAID")
    controller.repo = repo

    result = controller.delete_sale(1)

    assert result is False

def test_apply_discount_valid():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale(status="OPEN")
    controller.repo = repo

    result = controller.apply_discount_to_sale(1, 0.2)

    assert result is True
    assert repo.sale.discount_rate == 0.2


def test_apply_discount_invalid_rate():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale(status="OPEN")
    controller.repo = repo

    assert controller.apply_discount_to_sale(1, -1.0) is False
    assert controller.apply_discount_to_sale(1, 2.0) is False

def test_close_sale_open_success():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale(status="OPEN")
    controller.repo = repo

    result = controller.close_sale(1)

    assert result is True
    assert repo.sale.status == "PENDING"

def test_compute_points_success():
    fake_db = FakeDB()
    controller = SaleController(fake_db)
    repo = FakeSaleRepository(fake_db)
    repo.sale = FakeSale()
    controller.repo = repo

    result = controller.compute_points(1)

    assert result == {"points": 10}
