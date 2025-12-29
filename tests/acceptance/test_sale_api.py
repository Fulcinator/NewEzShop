from unittest.mock import MagicMock
import pytest
from app.config.config import ROUTES
from datetime import datetime

def sale_transaction_dto(
    sale_id: int = 1,
    status: str = "OPEN",
    cost: float = 0.0,
    discount_rate: float = 0.0
):
    return {
        "sale_transaction_id": sale_id,
        "status": status,
        "cost": cost,
        "paymentType": None,
        "discountRate": discount_rate,
        "created_at": datetime.utcnow().isoformat(),
        "closed_at": None,
        "loyalty_card_id": None,
        "lines": []
    }

BASE_SALES = ROUTES["V1_SALES"]


def auth_header(auth_tokens, role="admin"):
    return {"Authorization": auth_tokens[role]}


def test_start_sale_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.start_sale.return_value = sale_transaction_dto(1)

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.post(
        BASE_SALES,
        headers={"Authorization": auth_tokens["admin"]}
    )

    assert response.status_code == 201
    assert response.json()["sale_transaction_id"] == 1




def test_get_all_sales(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_all_sales.return_value = [
        sale_transaction_dto(1),
        sale_transaction_dto(2)
    ]

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.get(
        BASE_SALES,
        headers={"Authorization": auth_tokens["admin"]}
    )

    assert response.status_code == 200
    assert len(response.json()) == 2



def test_get_sale_found(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_sale.return_value = sale_transaction_dto(1)

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_SALES}/1",
        headers={"Authorization": auth_tokens["admin"]}
    )

    assert response.status_code == 200
    assert response.json()["sale_transaction_id"] == 1



def test_get_sale_not_found(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_sale.return_value = None

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_SALES}/999",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 404


def test_delete_paid_sale_fails(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.delete_sale.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_SALES}/1",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420


def test_add_product_invalid_amount(client, auth_tokens):
    response = client.post(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 0},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400


def test_add_product_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.add_product_to_sale.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.post(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 2},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.parametrize("rate", [-0.1, 1.5])
def test_apply_discount_invalid_rate(client, auth_tokens, rate):
    response = client.patch(
        f"{BASE_SALES}/1/discount",
        params={"discount_rate": rate},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400


def test_close_sale_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.close_sale.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/close",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_pay_sale_not_closed(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.pay_sale.return_value = None

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/pay",
        params={"cash_amount": 100},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420


def test_compute_points_sale_not_found(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.compute_points.return_value = None

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_SALES}/1/points",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 404


def test_remove_product_invalid_amount(client, auth_tokens):
    response = client.delete(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 0},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400

def test_remove_product_closed_sale_fails(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.remove_product_from_sale.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 1},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420

def test_remove_product_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.remove_product_from_sale.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 1},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.parametrize("rate", [-0.2, 1.1])
def test_apply_product_discount_invalid_rate(client, auth_tokens, rate):
    response = client.patch(
        f"{BASE_SALES}/1/items/ABC/discount",
        params={"discount_rate": rate},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400

def test_apply_product_discount_closed_sale(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.apply_discount_to_product.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/items/ABC/discount",
        params={"discount_rate": 0.1},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420

def test_apply_product_discount_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.apply_discount_to_product.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/items/ABC/discount",
        params={"discount_rate": 0.2},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

def test_apply_discount_closed_sale_returns_420(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.apply_discount_to_sale.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/discount",
        params={"discount_rate": 0.2},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420
    assert response.json()["detail"] == "Cannot modify a closed sale"

def test_apply_discount_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.apply_discount_to_sale.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/discount",
        params={"discount_rate": 0.15},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}

def test_pay_sale_negative_cash_amount(client, auth_tokens):
    response = client.patch(
        f"{BASE_SALES}/1/pay",
        params={"cash_amount": -10},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400
    assert "Cash amount cannot be negative" in response.text

def test_apply_discount_closed_sale_420(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.apply_discount_to_sale.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_SALES}/1/discount",
        params={"discount_rate": 0.2},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420
    assert response.json()["detail"] == "Cannot modify a closed sale"

def test_add_product_non_open_sale_420(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.add_product_to_sale.return_value = False

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.post(
        f"{BASE_SALES}/1/items",
        params={"barcode": "ABC", "amount": 1},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420
    assert response.json()["detail"] == "Cannot modify a non-open sale"

def test_delete_sale_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.delete_sale.return_value = True

    monkeypatch.setattr(
        "app.routes.sale_route.SaleController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_SALES}/1",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json() == {"success": True}
