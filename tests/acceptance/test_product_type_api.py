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
    barcode: str = "ABC123",
    name: str = "Test Product",
    description: str | None = "Test description",
    quantity: int = 10
):
    return {
        "id": product_type_id,
        "barcode": barcode,
        "name": name,
        "description": description,
        "sellPrice": 9.99,
        "quantity": quantity,
        "discountRate": None,
        "notes": None,
        "position_id": None,
    }


# =================================================
# CREATE PRODUCT TYPE
# =================================================

def test_create_product_type_success_admin(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(product_type_id=1)

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.create",
        async_mock
    )

    response = client.post(
        BASE_PRODUCTS,
        json={
            "barcode": "ABC123",
            "name": "Test Product",
            "description": "Test description",
            "sellPrice": 9.99,
            "quantity": 10,
        },
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 201
    assert response.json()["id"] == 1


def test_create_product_type_forbidden_cashier(client, auth_tokens):
    response = client.post(
        BASE_PRODUCTS,
        json={
            "barcode": "ABC123",
            "name": "Test Product",
            "description": "Test description",
            "sellPrice": 9.99,
            "quantity": 10,
        },
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403


# =================================================
# UPDATE PRODUCT TYPE
# =================================================

def test_update_product_type_success_manager(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = product_type_response_dto(
        product_type_id=1,
        name="Updated Product"
    )

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.update",
        async_mock
    )

    response = client.put(
        f"{BASE_PRODUCTS}/1",
        json={
            "name": "Updated Product",
            "description": None,
            "sellPrice": 8.99,
            "quantity": 5,
        },
        headers=auth_header(auth_tokens, role="manager")
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"


def test_update_product_type_forbidden_cashier(client, auth_tokens):
    response = client.put(
        f"{BASE_PRODUCTS}/1",
        json={"name": "Hack"},
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403


# =================================================
# DELETE PRODUCT TYPE
# =================================================

def test_delete_product_type_success_admin(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = None

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.delete",
        async_mock
    )

    response = client.delete(
        f"{BASE_PRODUCTS}/1",
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_product_type_forbidden_cashier(client, auth_tokens):
    response = client.delete(
        f"{BASE_PRODUCTS}/1",
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403


# =================================================
# LIST PRODUCT TYPES
# =================================================

def test_list_product_types_admin(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = [
        product_type_response_dto(1),
        product_type_response_dto(2),
    ]

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.list_all",
        async_mock
    )

    response = client.get(
        BASE_PRODUCTS,
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_product_types_cashier_allowed(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = [product_type_response_dto(1)]

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.list_all",
        async_mock
    )

    response = client.get(
        BASE_PRODUCTS,
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


# =================================================
# SEARCH PRODUCT TYPES
# =================================================

def test_search_product_types_by_barcode(client, auth_tokens, monkeypatch):
    async_mock = AsyncMock()
    async_mock.return_value = [
        product_type_response_dto(barcode="XYZ999")
    ]

    monkeypatch.setattr(
        "app.routes.product_type_route.controller.search",
        async_mock
    )

    response = client.get(
        f"{BASE_PRODUCTS}/search",
        params={"barcode": "XYZ999"},
        headers=auth_header(auth_tokens, role="admin")
    )

    assert response.status_code == 200
    assert response.json()[0]["barcode"] == "XYZ999"


def test_search_product_types_forbidden_cashier(client, auth_tokens):
    response = client.get(
        f"{BASE_PRODUCTS}/search",
        params={"barcode": "ABC123"},
        headers=auth_header(auth_tokens, role="cashier")
    )

    assert response.status_code == 403
