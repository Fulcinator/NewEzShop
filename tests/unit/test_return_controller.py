from app.controllers.return_controller import ReturnController
from tests.unit.fakes.fake_return_repo import FakeReturnRepository
from tests.unit.fakes.fake_db import FakeDB

def make_controller():
    db = FakeDB()
    controller = ReturnController(db)
    controller.repo = FakeReturnRepository(db) 
    return controller, db


# ---------- Tests ----------

def test_start_return_success():
    controller, db = make_controller()

    class FakeSale:
        id = 1
        status = "PAID"

    db.sale = FakeSale()

    result = controller.start_return(sale_id=1)

    assert result is not None
    assert result.status == "OPEN"


def test_start_return_fails_if_sale_not_paid():
    controller, db = make_controller()

    class FakeSale:
        id = 1
        status = "OPEN"

    db.sale = FakeSale()

    result = controller.start_return(1)

    assert result is None


def test_get_all_returns():
    controller, db = make_controller()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    returns = controller.get_all_returns()

    assert len(returns) == 1


def test_get_return_by_id():
    controller, db = make_controller()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    ret = controller.get_return(1)

    assert ret is not None


def test_delete_return_success():
    controller, db = make_controller()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    result = controller.delete_return(1)

    assert result is True
    assert controller.repo.return_obj is None


def test_add_product_to_return_success():
    controller, db = make_controller()

    class FakeProduct:
        id = 1
        barcode = "123"
        quantity = 10

    class FakeSaleLine:
        product_type_id = 1
        quantity = 5

    class FakeSale:
        id = 1
        status = "PAID"
        sale_lines = [FakeSaleLine()]

    db.product = FakeProduct()
    db.sale = FakeSale()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    result = controller.add_product_to_return(
        return_id=1,
        barcode="123",
        amount=2
    )

    assert result is True
    assert len(controller.repo.return_obj.returned_products) == 1


def test_remove_product_from_return_success():
    controller, db = make_controller()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    controller.repo.add_returned_product(1, {
        "product_type_id": 1,
        "quantity": 3
    })

    class FakeProduct:
        id = 1
        barcode = "123"

    db.product = FakeProduct()

    result = controller.remove_product_from_return(
        return_id=1,
        barcode="123",
        amount=3
    )

    assert result is True
    assert len(controller.repo.return_obj.returned_products) == 0


def test_close_return_success():
    controller, db = make_controller()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "OPEN"
    })

    class FakeProduct:
        id = 1
        quantity = 5

    db.product = FakeProduct()

    controller.repo.add_returned_product(1, {
        "product_type_id": 1,
        "quantity": 2
    })

    result = controller.close_return(1)

    assert result is True
    assert controller.repo.return_obj.status == "CLOSED"


def test_reimburse_return_success():
    controller, db = make_controller()

    class FakeSaleLine:
        product_type_id = 1
        unit_price = 10.0
        discount_rate = 0.1

    class FakeSale:
        id = 1
        status = "PAID"
        discount_rate = 0.2
        sale_lines = [FakeSaleLine()]

    class FakeSystemInfo:
        balance = 100.0

    db.sale = FakeSale()
    db.system_info = FakeSystemInfo()

    controller.repo.create_return({
        "sale_transaction_id": 1,
        "status": "CLOSED"
    })

    controller.repo.add_returned_product(1, {
        "product_type_id": 1,
        "quantity": 2
    })

    controller.repo.return_obj.status = "CLOSED"

    result = controller.reimburse_return(1)

    assert result is not None
    assert "refund_amount" in result
    assert db.system_info.balance < 100