import pytest
import random
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
            "description": f"Product {barcode}",
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
            "barcode": "123456789012",  # Valid 12-digit barcode
            "description": "Test Product",
            "price_per_unit": 12.5,
            "quantity": 50,
            "position": "1-A-1001",
        },
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 201)


@pytest.mark.asyncio
def test_get_product_by_id(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"1111111{random.randint(10000, 99999)}"
    created = create_product(
        client,
        auth_tokens["admin"],
        product_id=product_id,
        barcode=barcode,  # Valid 12-digit barcode
    )

    real_id = created["id"]

    response = client.get(
        f"{PRODUCTS_BASE}/{real_id}",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert response.json()["barcode"] == barcode




@pytest.mark.asyncio
def test_get_product_by_barcode(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"2222222{random.randint(10000, 99999)}"
    create_product(
        client,
        auth_tokens["admin"],
        product_id=product_id,
        barcode=barcode,  # Valid 12-digit barcode
    )

    response = client.get(
        f"{PRODUCTS_BASE}/barcode/{barcode}",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert response.json()["barcode"] == barcode




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
    product_id = random.randint(10000, 99999)
    barcode = f"3333333{random.randint(10000, 99999)}"
    create_product(client, auth_tokens["admin"], product_id=product_id, barcode=barcode)

    response = client.get(
        f"{PRODUCTS_BASE}/search",
        params={"description": barcode},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert any(p["barcode"] == barcode for p in response.json())


@pytest.mark.asyncio
def test_update_product(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"4444444{random.randint(10000, 99999)}"
    created = create_product(client, auth_tokens["admin"], product_id=product_id, barcode=barcode)

    response = client.put(
        f"{PRODUCTS_BASE}/{created['id']}",
        json={
            "description": "Updated Description",
            "price_per_unit": 20.0,
        },
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 201


@pytest.mark.asyncio
def test_patch_product_position(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"5555555{random.randint(10000, 99999)}"
    product = create_product(client, auth_tokens["admin"], product_id=product_id, barcode=barcode)

    response = client.patch(
        f"{PRODUCTS_BASE}/{product['id']}/position",
        json={"position": "1-B-2006"},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 201)
    assert response.json()["success"] is True


@pytest.mark.asyncio
def test_patch_product_quantity(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"6666666{random.randint(10000, 99999)}"
    product = create_product(client, auth_tokens["admin"], product_id=product_id, barcode=barcode)

    response = client.patch(
        f"{PRODUCTS_BASE}/{product['id']}/quantity",
        params={"quantity": 250},
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 201
    assert response.json()["success"] is True


@pytest.mark.asyncio
def test_delete_product(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"7777777{random.randint(10000, 99999)}"
    product = create_product(client, auth_tokens["admin"], product_id=product_id, barcode=barcode)

    response = client.delete(
        f"{PRODUCTS_BASE}/{product['id']}",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code in (200, 204)
