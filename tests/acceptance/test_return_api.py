from unittest.mock import MagicMock
from datetime import datetime
import pytest
from app.config.config import ROUTES

BASE_RETURNS = ROUTES["V1_RETURNS"]


def auth_header(auth_tokens, role="admin"):
    return {"Authorization": auth_tokens[role]}


# --- DTO factory (MUST match ReturnTransactionDTO exactly) ---
def return_transaction_dto(
    return_id: int = 1,
    sale_id: int = 1,
    status: str = "OPEN",
):
    return {
        "return_transaction_id": return_id,   # alias for id
        "sale_transaction_id": sale_id,
        "status": status,
        "created_at": datetime.utcnow().isoformat(),
        "closed_at": None,
        "product_lines": [],
    }


# -------------------------------
# START RETURN
# -------------------------------

def test_start_return_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.start_return.return_value = return_transaction_dto(
        return_id=1,
        sale_id=10
    )

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.post(
        BASE_RETURNS,
        params={"sale_id": 10},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 201
    assert response.json()["return_transaction_id"] == 1
    assert response.json()["sale_transaction_id"] == 10


def test_start_return_not_allowed(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.start_return.return_value = None

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.post(
        BASE_RETURNS,
        params={"sale_id": 99},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420


# -------------------------------
# GET RETURNS
# -------------------------------

def test_get_all_returns(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_all_returns.return_value = [
        return_transaction_dto(1, 5),
        return_transaction_dto(2, 6),
    ]

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.get(
        BASE_RETURNS,
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_return_found(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_return.return_value = return_transaction_dto(1, 5)

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_RETURNS}/1",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["return_transaction_id"] == 1


def test_get_return_not_found(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_return.return_value = None

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_RETURNS}/999",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 404


def test_get_returns_by_sale(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.get_returns_by_sale.return_value = [
        return_transaction_dto(1, sale_id=5),
        return_transaction_dto(2, sale_id=5),
    ]

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.get(
        f"{BASE_RETURNS}/sale/5",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


# -------------------------------
# DELETE RETURN
# -------------------------------

def test_delete_return_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.delete_return.return_value = True

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_RETURNS}/1",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_delete_return_reimbursed_fails(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.delete_return.return_value = False

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_RETURNS}/1",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420


# -------------------------------
# ADD / REMOVE ITEMS
# -------------------------------

def test_add_product_invalid_amount(client, auth_tokens):
    response = client.post(
        f"{BASE_RETURNS}/1/items",
        params={"barcode": "ABC", "amount": 0},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 400


def test_add_product_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.add_product_to_return.return_value = True

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.post(
        f"{BASE_RETURNS}/1/items",
        params={"barcode": "ABC", "amount": 2},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 201
    assert response.json()["success"] is True


def test_remove_product_from_closed_return_fails(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.remove_product_from_return.return_value = False

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.delete(
        f"{BASE_RETURNS}/1/items",
        params={"barcode": "ABC", "amount": 1},
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 420


# -------------------------------
# CLOSE & REIMBURSE
# -------------------------------

def test_close_return_success(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.close_return.return_value = True

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_RETURNS}/1/close",
        headers=auth_header(auth_tokens)
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_reimburse_return_success_admin(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.reimburse_return.return_value = return_transaction_dto(
        return_id=1,
        sale_id=5,
        status="REIMBURSED"
    )

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_RETURNS}/1/reimburse",
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REIMBURSED"


def test_reimburse_return_not_closed_fails(client, auth_tokens, monkeypatch):
    mock_controller = MagicMock()
    mock_controller.reimburse_return.return_value = None

    monkeypatch.setattr(
        "app.routes.return_route.ReturnController",
        lambda db: mock_controller
    )

    response = client.patch(
        f"{BASE_RETURNS}/1/reimburse",
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 420
