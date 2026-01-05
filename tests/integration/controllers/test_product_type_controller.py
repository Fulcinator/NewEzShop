import pytest
from app.config.config import ROUTES

PRODUCTS_BASE = ROUTES["V1_PRODUCT_TYPES"]


def auth(token: str):
    return {"Authorization": token}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def create_product(client, token, *, product_id: int, barcode: str):
    """
    Create a product and return the created DTO.
    We send `product_id` because the API requires it,
    but we NEVER assume it will be the persisted ID.
    """
    response = client.post(
        PRODUCTS_BASE,
        json={
            "id": product_id,
            "barcode": barcode,
            "name": f"Product {barcode}",
            "description": f"Description for {barcode}",
            "price_per_unit": 10.0,
            "quantity": 100,
            "position": f"1-A-{1000 + product_id}",  # globally unique
        },
        headers=auth(token),
    )
    assert response.status_code in (200, 201), response.text
    return response.json()




# =====================================================================
# TESTS
# =====================================================================

@pytest.mark.asyncio
def test_create_product(client, auth_tokens):
    response = client.post(
        PRODUCTS_BASE,
        json={
            "id": 1,
            "barcode": "P-100",
            "name": "Test Product",
            "description": "Test Description",
            "price_per_unit": 12.5,
            "quantity": 50,
            "position": "1-A-1001",
        },
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
def test_get_product_by_id(client, auth_tokens):
    created = create_product(
        client,
        auth_tokens["admin"],
        product_id=101,
        barcode="P-101",
    )

    real_id = created["id"]

    response = client.get(
        f"{PRODUCTS_BASE}/{real_id}",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert response.json()["barcode"] == "P-101"




@pytest.mark.asyncio
def test_get_product_by_barcode(client, auth_tokens):
    created = create_product(
        client,
        auth_tokens["admin"],
        product_id=102,
        barcode="P-102",
    )

    response = client.get(
        f"{PRODUCTS_BASE}/barcode/P-102",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]




@pytest.mark.asyncio
def test_list_all_products(client, auth_tokens):
    response = client.get(
        f"{PRODUCTS_BASE}/",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
def test_search_products_by_description(client, auth_tokens):
    create_product(client, auth_tokens["admin"], product_id=4, barcode="P-SEARCH")

    response = client.get(
        f"{PRODUCTS_BASE}/search",
        params={"description": "SEARCH"},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert any(p["barcode"] == "P-SEARCH" for p in response.json())


@pytest.mark.asyncio
def test_update_product(client, auth_tokens):
    create_product(client, auth_tokens["admin"], product_id=5, barcode="P-UPDATE")

    response = client.put(
        f"{PRODUCTS_BASE}/5",
        json={
            "name": "Updated Name",
            "description": "Updated Description",
            "price_per_unit": 20.0,
        },
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200 


@pytest.mark.asyncio
def test_patch_product_position(client, auth_tokens):
    create_product(client, auth_tokens["admin"], product_id=6, barcode="P-POS")

    response = client.patch(
        f"{PRODUCTS_BASE}/6/position",
        json={"position": "1-B-2006"},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 201)
    assert response.json()["success"] is True


@pytest.mark.asyncio
def test_patch_product_quantity(client, auth_tokens):
    create_product(client, auth_tokens["admin"], product_id=7, barcode="P-QTY")

    response = client.patch(
        f"{PRODUCTS_BASE}/7/quantity",
        json={"quantity": 250},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 201)
    assert response.json()["success"] is True


@pytest.mark.asyncio
def test_delete_product(client, auth_tokens):
    create_product(client, auth_tokens["admin"], product_id=8, barcode="P-DEL")

    response = client.delete(
        f"{PRODUCTS_BASE}/8",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 204)
