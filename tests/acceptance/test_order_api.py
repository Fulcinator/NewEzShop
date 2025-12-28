import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import text
from main import app
from app.database.database import engine 

client = TestClient(app)
BASE_URL = "/api/v1/orders"

def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}

@pytest.fixture(autouse=True)
async def seed_data():
    """Seeds the DB with mandatory fields for ProductTypes."""
    async with engine.connect() as connection:
        await connection.execute(text("DELETE FROM product_types"))
        await connection.execute(text("DELETE FROM shops"))
        
        await connection.execute(text("INSERT INTO shops DEFAULT VALUES"))
        await connection.commit()
        
        res = await connection.execute(text("SELECT last_insert_rowid()"))
        shop_id = res.scalar()
        
        unique_name = f"Test_Product_{uuid.uuid4().hex[:6]}"
        await connection.execute(text("""
            INSERT INTO product_types (name, barcode, sellPrice, quantity, shop_id) 
            VALUES (:name, :barcode, :price, :qty, :sid)
        """), {
            "name": unique_name,
            "barcode": uuid.uuid4().hex[:12],
            "price": 25.0,
            "qty": 100,
            "sid": shop_id
        })
        await connection.commit()

# ---------------------------------------------------------
# ORDER ACCEPTANCE TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_order_lifecycle_acceptance(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    
    async with engine.connect() as conn:
        res_p = await conn.execute(text("SELECT rowid FROM product_types LIMIT 1"))
        product_id = res_p.scalar()
        res_s = await conn.execute(text("SELECT rowid FROM shops LIMIT 1"))
        shop_id = res_s.scalar()

    payload = {
        "product_type_id": product_id, 
        "quantity": 10,
        "supplier": "Test Supplier",
        "price_per_unit": 10.0,
        "shop_id": shop_id 
    }
    
    resp = client.post(f"{BASE_URL}/reorder-warning", json=payload, headers=headers)
    assert resp.status_code == 201, f"Failed: {resp.json()}"
    
    order_data = resp.json()
    order_id = order_data.get("id") or order_data.get("order_id")
    
    # Transitions
    assert client.post(f"{BASE_URL}/{order_id}/pay", headers=headers).status_code == 200
    assert client.post(f"{BASE_URL}/{order_id}/arrival", headers=headers).status_code == 200

@pytest.mark.asyncio
async def test_list_orders_permissions(auth_tokens):
    """
    If this fails with TypeError, check that:
    1. Route doesn't pass 'status' module.
    2. Repository.list_orders() accepts an optional status argument.
    """
    # Admin - Success (Checks technical plumbing)
    resp_admin = client.get(f"{BASE_URL}/", headers=auth_header(auth_tokens, "admin"))
    assert resp_admin.status_code == 200
    assert isinstance(resp_admin.json(), list)

    # Cashier - Forbidden (Checks security plumbing)
    resp_cashier = client.get(f"{BASE_URL}/", headers=auth_header(auth_tokens, "cashier"))
    assert resp_cashier.status_code == 403