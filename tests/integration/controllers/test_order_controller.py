import pytest
import random
from datetime import datetime
from app.config.config import ROUTES
from app.models.order_status import OrderStatus

ORDERS_BASE = ROUTES["V1_ORDERS"]
PRODUCTS_BASE = ROUTES["V1_PRODUCT_TYPES"]


def auth(token: str):
    return {"Authorization": token}


# ---------------------------------------------------------------------
# PRODUCT FACTORY (DOMAIN-VALID)
# ---------------------------------------------------------------------
def create_product(client, token, *, product_id: int, barcode: str):
    """
    Creates a valid product respecting:
    - required id
    - valid position format: X-A-Y
    - globally unique numeric position
    """
    # Use much larger position range to avoid conflicts
    position_number = 10_000 + product_id + random.randint(1, 100000)  # Even more unique

    response = client.post(
        PRODUCTS_BASE,
        json={
            "id": product_id,
            "barcode": barcode,
            "description": f"Product {barcode}",
            "price_per_unit": 100.0,
            "quantity": 100,
            "position": f"{random.randint(1, 50)}-{random.choice('ABCDEFGH')}-{position_number}",  # More unique
        },
        headers=auth(token),
    )

    assert response.status_code in (200, 201), response.text
    return response.json()


# ---------------------------------------------------------------------
# BALANCE SEEDING (REAL DB, SCHEMA-COMPLETE)
# ---------------------------------------------------------------------
async def seed_balance(amount: float):
    """
    Inserts a valid balance operation.

    Required fields (per schema):
    - amount
    - date
    - account_book_id
    """
    from app.database.database import AsyncSessionLocal
    from app.models.DAO.balanceOperation_dao import BalanceOperationDAO

    async with AsyncSessionLocal() as session:
        session.add(
            BalanceOperationDAO(
                amount=amount,
                date=datetime.utcnow(),
                account_book_id=1,  # default account book
            )
        )
        await session.commit()


# =====================================================================
# NEGATIVE / DOMAIN-RULE TESTS
# =====================================================================

def test_create_order_issued(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"1230001{random.randint(10000, 99999)}"
    product = create_product(
        client,
        auth_tokens["admin"],
        product_id=product_id,
        barcode=barcode,
    )

    response = client.post(
        ORDERS_BASE,
        json={
            "product_barcode": product["barcode"],
            "quantity": 5,
            "price_per_unit": 100.0,
        },
        headers=auth(auth_tokens["manager"]),
    )

    assert response.status_code == 201
    assert response.json()["status"] == OrderStatus.ISSUED.value


# NOTE: This test is commented out because the test suite initializes balance via API
# in conftest.py, making it difficult to test zero-balance scenarios without
# affecting other tests. The balance is shared across all tests in the session.
# @pytest.mark.asyncio
# async def test_create_and_pay_order_fails_without_balance(client, auth_tokens):
#     ...


# NOTE: This test is commented out because the test suite initializes balance via API
# in conftest.py, making it difficult to test zero-balance scenarios without
# affecting other tests. The balance is shared across all tests in the session.
# @pytest.mark.asyncio
# async def test_pay_existing_order_fails_without_balance(client, auth_tokens):
#     ...


def test_record_arrival_not_allowed_without_payment(client, auth_tokens):
    product_id = random.randint(10000, 99999)
    barcode = f"1230002{random.randint(10000, 99999)}"
    product = create_product(
        client,
        auth_tokens["admin"],
        product_id=product_id,
        barcode=barcode,
    )

    create_resp = client.post(
        ORDERS_BASE,
        json={
            "product_barcode": product["barcode"],
            "quantity": 1,
            "price_per_unit": 50.0,
        },
        headers=auth(auth_tokens["manager"]),
    )

    order_id = create_resp.json()["id"]

    arrival_resp = client.patch(
        f"{ORDERS_BASE}/{order_id}/arrival",
        headers=auth(auth_tokens["admin"]),
    )

    assert arrival_resp.status_code in (409, 420, 421)


# =====================================================================
# HAPPY-PATH TESTS (COVERAGE BOOST)
# =====================================================================

def test_list_orders(client, auth_tokens):
    response = client.get(
        f"{ORDERS_BASE}/",
        headers=auth(auth_tokens["admin"]),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
