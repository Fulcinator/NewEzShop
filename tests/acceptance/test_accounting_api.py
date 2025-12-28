import pytest
from fastapi.testclient import TestClient
from main import app
from app.config.config import ROUTES

client = TestClient(app)
BASE_URL = ROUTES["V1_GENERAL"]

def auth_header(tokens, role: str):
    return {"Authorization": tokens[role]}

# ---------------------------------------------------------
# ACCOUNTING & BALANCE ACCEPTANCE TESTS
# ---------------------------------------------------------

@pytest.mark.asyncio
async def test_balance_lifecycle_admin(auth_tokens):
    """
    Tests the full accounting lifecycle as an Administrator.
    Ensures that balance persists across different requests.
    """
    headers = auth_header(auth_tokens, "admin")

    # 1. RESET BALANCE
    # Should set balance to 0.0 and return 205
    reset_resp = client.post(f"{BASE_URL}/balance/reset", headers=headers)
    assert reset_resp.status_code == 205

    # 2. VERIFY BASELINE
    get_init = client.get(f"{BASE_URL}/balance", headers=headers)
    assert get_init.status_code == 200
    assert float(get_init.json()["balance"]) == 0.0

    # 3. SET BALANCE
    # amount: float = Query(...) -> /api/v1/general/balance/set?amount=5000.75
    target_amount = 5000.75
    set_resp = client.post(
        f"{BASE_URL}/balance/set", 
        params={"amount": target_amount}, 
        headers=headers
    )
    assert set_resp.status_code == 201

    # 4. FINAL VERIFICATION
    # If this fails with 0.0, the 'set' operation did not commit to the DB.
    get_final = client.get(f"{BASE_URL}/balance", headers=headers)
    assert get_final.status_code == 200
    
    data = get_final.json()
    actual_balance = float(data["balance"])
    
    assert actual_balance == target_amount, (
        f"Persistence Error: Expected balance {target_amount}, "
        f"but database returned {actual_balance}. Check your Repository.commit()."
    )

@pytest.mark.asyncio
async def test_accounting_rbac_protection(auth_tokens):
    """
    Verifies that only Administrators can access accounting.
    """
    for role in ["manager", "cashier"]:
        headers = auth_header(auth_tokens, role)
        resp = client.get(f"{BASE_URL}/balance", headers=headers)
        assert resp.status_code == 403

@pytest.mark.asyncio
async def test_set_balance_missing_param(auth_tokens):
    """Checks for 422 error when amount is missing."""
    headers = auth_header(auth_tokens, "admin")
    resp = client.post(f"{BASE_URL}/balance/set", headers=headers)
    assert resp.status_code == 422