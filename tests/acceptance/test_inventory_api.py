from unittest.mock import AsyncMock
import pytest
from app.config.config import ROUTES

BASE_PRODUCTS = ROUTES["V1_PRODUCT_TYPES"]


def auth_header(auth_tokens, role="admin"):
    return {"Authorization": auth_tokens[role]}


# -------------------------------------------------
# DTO factory (matches ProductTypeResponseDTO)
# -------------------------------------------------
def product_type_response_dto(
    product_type_id: int = 1,
    quantity: int = 10,
    position_id: int | None = None
):
    return {
        "id": product_type_id,
        "barcode": "ABC123",
        "name": "Test Product",
        "description": "Test description",
        "sellPrice": 9.99,
        "quantity": quantity,
        "discountRate": None,
        "notes": None,
        "position_id": position_id,
    }


# =================================================
# MODIFY QUANTITY
# =================================================

def test_modify_quantity_success_admin(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(
        product_type_id=1,
        quantity=20
    )

    monkeypatch.setattr(
        "app.routes.inventory_route.controller.update_quantity",
        async_mock
    )

    response = client.put(
        f"{BASE_PRODUCTS}/1/quantity",
        json={"new_quantity": 20},   # ✅ FIXED
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 20


def test_modify_quantity_success_shop_manager(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(
        product_type_id=2,
        quantity=15
    )

    monkeypatch.setattr(
        "app.routes.inventory_route.controller.update_quantity",
        async_mock
    )

    response = client.put(
        f"{BASE_PRODUCTS}/2/quantity",
        json={"new_quantity": 15},   # ✅ FIXED
        headers=auth_header(auth_tokens, role="manager")
    )

    assert response.status_code == 200
    assert response.json()["quantity"] == 15


def test_modify_quantity_forbidden_for_cashier(client, auth_tokens):
    response = client.put(
        f"{BASE_PRODUCTS}/1/quantity",
        json={"new_quantity": 5},
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403


# =================================================
# MODIFY POSITION
# =================================================

def test_modify_position_success_admin(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(
        product_type_id=1,
        position_id=100
    )

    monkeypatch.setattr(
        "app.routes.inventory_route.controller.update_position",
        async_mock
    )

    response = client.put(
        f"{BASE_PRODUCTS}/1/position",
        json={
            "aisleID": 1,
            "rackID": 2,
            "levelID": 3
        },  # ✅ FIXED
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 200
    assert response.json()["position_id"] == 100


def test_modify_position_success_shop_manager(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(
        product_type_id=3,
        position_id=200
    )

    monkeypatch.setattr(
        "app.routes.inventory_route.controller.update_position",
        async_mock
    )

    response = client.put(
        f"{BASE_PRODUCTS}/3/position",
        json={
            "aisleID": 4,
            "rackID": 5,
            "levelID": 6
        },  # ✅ FIXED
        headers=auth_header(auth_tokens, role="manager")
    )

    assert response.status_code == 200
    assert response.json()["position_id"] == 200


def test_modify_position_forbidden_for_cashier(client, auth_tokens):
    response = client.put(
        f"{BASE_PRODUCTS}/1/position",
        json={
            "aisleID": 1,
            "rackID": 1,
            "levelID": 1
        },
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403
