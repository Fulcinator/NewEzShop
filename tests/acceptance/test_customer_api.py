import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import text
from main import app
from app.config.config import ROUTES
from app.database.database import engine

client = TestClient(app)
BASE_URL = ROUTES["V1_CUSTOMERS"]


def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}


@pytest.fixture(autouse=True)
async def seed_dependencies():
    async with engine.connect() as conn:
        await conn.execute(text("INSERT INTO shops DEFAULT VALUES"))
        await conn.commit()
        res = await conn.execute(text("SELECT last_insert_rowid()"))
        pytest.shop_id = res.scalar()

@pytest.fixture(autouse=True)
async def clean_customer_tables():
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM loyalty_cards"))
        await conn.execute(text("DELETE FROM customers"))

# HELPERS

def create_customer(headers):
    unique = uuid.uuid4().hex[:6]

    payload = {
        "name": f"Jane_{unique}",          
        "surname": f"Doe_{unique}",        
        "email": f"user_{unique}@test.com",
        "phone": str(uuid.uuid4().int)[:10],
    }

    resp = client.post(BASE_URL, json=payload, headers=headers)
    assert resp.status_code == 201, f"Create failed: {resp.json()}"
    return resp.json()


def create_card(headers):
    payload = {
        "card_code": uuid.uuid4().hex[:10].upper(),
        "points": 0,
        "shop_id": pytest.shop_id,
    }
    resp = client.post(f"{BASE_URL}/cards", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


#tests
@pytest.mark.asyncio
async def test_get_customer_success(auth_tokens):
    headers = auth_header(auth_tokens, "admin")

    customer = create_customer(headers)

    resp = client.get(f"{BASE_URL}/{customer['id']}", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["id"] == customer["id"]
    assert resp.json()["name"] == customer["name"]



@pytest.mark.asyncio
async def test_update_customer_success(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    customer = create_customer(headers)

    resp = client.put(
        f"{BASE_URL}/{customer['id']}",
        json={"name": "UpdatedName"},
        headers=headers
    )

    assert resp.status_code == 200
    assert resp.json()["name"] == "UpdatedName"



@pytest.mark.asyncio
async def test_delete_customer_success(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    customer = create_customer(headers)

    resp = client.delete(f"{BASE_URL}/{customer['id']}", headers=headers)
    assert resp.status_code == 204

    # verify deletion
    resp = client.get(f"{BASE_URL}/{customer['id']}", headers=headers)
    assert resp.status_code == 404



@pytest.mark.asyncio
async def test_delete_customer_success(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    customer = create_customer(headers)

    resp = client.delete(f"{BASE_URL}/{customer['id']}", headers=headers)
    assert resp.status_code == 204

    # verify deletion
    resp = client.get(f"{BASE_URL}/{customer['id']}", headers=headers)
    assert resp.status_code == 404



@pytest.mark.asyncio
async def test_delete_customer_not_found(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    resp = client.delete(f"{BASE_URL}/999999", headers=headers)
    assert resp.status_code == 404



@pytest.mark.asyncio
async def test_create_loyalty_card_conflict(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    card = create_card(headers)

    payload = {
        "card_code": card["card_code"],
        "points": 0,
        "shop_id": pytest.shop_id,
    }

    resp = client.post(f"{BASE_URL}/cards", json=payload, headers=headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_attach_card_invalid_card_id(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    customer = create_customer(headers)

    resp = client.patch(
        f"{BASE_URL}/{customer['id']}/attach-card/not-a-number",
        headers=headers
    )

    assert resp.status_code == 400



@pytest.mark.asyncio
async def test_attach_card_not_found(auth_tokens):
    headers = auth_header(auth_tokens, "admin")
    customer = create_customer(headers)

    resp = client.patch(
        f"{BASE_URL}/{customer['id']}/attach-card/999999",
        headers=headers
    )

    assert resp.status_code == 404



# @pytest.mark.asyncio
# async def test_attach_card_conflict(auth_tokens):
#     headers = auth_header(auth_tokens, "admin")

#     customer1 = create_customer(headers)
#     customer2 = create_customer(headers)
#     card = create_card(headers)

#     # attach to first customer
#     resp = client.patch(
#         f"{BASE_URL}/{customer1['id']}/attach-card/{card['id']}",
#         headers=headers
#     )
#     assert resp.status_code == 200

#     # attach again to another customer → conflict
#     resp = client.patch(
#         f"{BASE_URL}/{customer2['id']}/attach-card/{card['id']}",
#         headers=headers
#     )

#     assert resp.status_code == 409


@pytest.mark.asyncio
async def test_modify_card_points_invalid_card_id(auth_tokens):
    headers = auth_header(auth_tokens, "admin")

    resp = client.patch(
        f"{BASE_URL}/cards/not-a-number?points=50",
        headers=headers,
    )

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_modify_card_points_not_found(auth_tokens):
    headers = auth_header(auth_tokens, "admin")

    resp = client.patch(
        f"{BASE_URL}/cards/999999?points=50",
        headers=headers,
    )

    assert resp.status_code == 404
