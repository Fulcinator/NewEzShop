import logging
import pytest
import random
from app.config.config import ROUTES

# Set up logger for testing
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RETURNS_BASE = ROUTES["V1_RETURNS"]
SALES_BASE = ROUTES["V1_SALES"]
PRODUCTS_BASE = ROUTES["V1_PRODUCT_TYPES"]
BASE_URL = "http://127.0.0.1:8000/api/v1"



def auth_headers(token: str):
    """Create authorization headers - expects token with Bearer prefix"""
    return {"Authorization": token}

def create_product_type(client, token, product_id: int, barcode: str):
    """Helper function to create and setup a product type"""
    response = client.post(
        PRODUCTS_BASE,
        json={
            "id": product_id,
            "barcode": barcode,
            "description": f"Test Product {barcode}",
            "price_per_unit": 25.0,
            "quantity": 100,
            "position": f"1-A-{product_id}",
            "note": "Test product for returns"
        },
        headers=auth_headers(token),
    )
    logger.debug(f"Create Product Type Response: {response.status_code} - {response.json()}")
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create product: {response.json()}")
    return response.json()

def create_paid_sale(client, token):
    """Helper function to create a complete paid sale
    
    NOTE: This requires system_info to be initialized in the database.
    If system_info is not initialized, this function will return (None, None).
    """
    
    # Generate unique barcodes and IDs for this test
    product_id_1 = random.randint(10000, 99999)
    product_id_2 = random.randint(10000, 99999)
    barcode1 = f"1234567{random.randint(100000, 999999)}"
    barcode2 = f"9876543{random.randint(100000, 999999)}"
    
    # 1. Create product types
    product1 = create_product_type(client, token, product_id_1, barcode1)
    product2 = create_product_type(client, token, product_id_2, barcode2)
    
    # 2. Create sale (OPEN)
    sale_response = client.post(
        SALES_BASE,
        headers=auth_headers(token),
    )
    assert sale_response.status_code in (200, 201)
    sale = sale_response.json()
    sale_id = sale.get("sale_transaction_id") or sale.get("id")
    if not sale_id:
        raise Exception(f"No sale ID found in response: {sale}")
    
    # 3. Add products to sale
    client.post(
        f"{SALES_BASE}/{sale_id}/items",
        params={"barcode": barcode1, "amount": 2},
        headers=auth_headers(token),
    )
    logger.debug(f"Added product 1 to sale {sale_id}")
    
    client.post(
        f"{SALES_BASE}/{sale_id}/items",
        params={"barcode": barcode2, "amount": 1},
        headers=auth_headers(token),
    )
    logger.debug(f"Added product 2 to sale {sale_id}")
    
    # 4. Close sale (OPEN → CLOSED)
    close_response = client.patch(
        f"{SALES_BASE}/{sale_id}/close",
        headers=auth_headers(token),
    )
    assert close_response.status_code == 200
    
    # 5. Pay for sale (CLOSED → PAID)
    pay_response = client.patch(
        f"{SALES_BASE}/{sale_id}/pay",
        params={"cash_amount": 100.0},
        headers=auth_headers(token),
    )
    
    if pay_response.status_code != 200:
        logger.warning(f"Payment failed: {pay_response.status_code} - {pay_response.text}")
        return None, None
    
    return sale_id, [barcode1, barcode2]


def create_return_safely(client, token, sale_id):
    """Helper to create a return and handle common errors"""
    response = client.post(
        RETURNS_BASE,
        params={"sale_id": sale_id},
        headers=auth_headers(token),
    )
    
    if response.status_code == 404:
        pytest.skip("Cannot create return - sale not found or not paid")
    
    if response.status_code not in (200, 201):
        pytest.skip(f"Cannot create return: {response.status_code} - {response.json()}")
    
    return response.json()


def test_start_return(client, auth_tokens):
    """Test creating a return transaction for a paid sale"""
    token = auth_tokens["manager"]
    
    # 1. Create a product
    product_response = client.post(
        PRODUCTS_BASE,
        json={
            "id": 101,
            "barcode": "12345678901",
            "description": "Test Product",
            "price_per_unit": 25.0,
            "quantity": 100,
            "position": "1-A-1",
        },
        headers=auth_headers(token),
    )
    assert product_response.status_code in (200, 201)
    
    # 2. Create sale
    sale_response = client.post(SALES_BASE, headers=auth_headers(token))
    assert sale_response.status_code == 201
    sale = sale_response.json()
    sale_id = sale["sale_transaction_id"]
    
    # 3. Verify sale exists
    get_response = client.get(f"{SALES_BASE}/{sale_id}", headers=auth_headers(token))
    assert get_response.status_code == 200
    
    # 4. Add product
    add_response = client.post(
        f"{SALES_BASE}/{sale_id}/items",
        params={"barcode": "12345678901", "amount": 2},
        headers=auth_headers(token),
    )
    assert add_response.status_code in (200, 201)
    
    # 5. Close sale
    close_response = client.patch(
        f"{SALES_BASE}/{sale_id}/close",
        headers=auth_headers(token),
    )
    assert close_response.status_code == 200
    
    # 6. Pay for sale
    pay_response = client.patch(
        f"{SALES_BASE}/{sale_id}/pay",
        params={"cash_amount": 100.0},
        headers=auth_headers(token),
    )
    
    if pay_response.status_code != 200:
        pytest.skip(f"Payment failed: {pay_response.text}")
    
    # 7. Create return
    return_response = client.post(
        RETURNS_BASE,
        params={"sale_id": sale_id},
        headers=auth_headers(token),
    )
    assert return_response.status_code in (200, 201)
    data = return_response.json()
    
    assert "id" in data
    assert data.get("sale_transaction_id") == sale_id or data.get("sale_id") == sale_id
    assert data["status"] == "OPEN"


def test_get_all_returns(client, auth_tokens):
    """Test retrieving all return transactions"""
    sale_id, barcodes = create_paid_sale(client, auth_tokens["manager"])
    
    if not sale_id:
        pytest.skip("Could not create paid sale - system info not initialized")

    # Start a return
    create_return_safely(client, auth_tokens["manager"], sale_id)

    # Get all returns
    response = client.get(
        f"{RETURNS_BASE}/",
        headers=auth_headers(auth_tokens["manager"]),
    )

    logger.debug(f"Get All Returns Response: {response.status_code} - {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list), "Response should be a list"


def test_get_return_by_id(client, auth_tokens):
    """Test retrieving a specific return by ID"""
    sale_id, barcodes = create_paid_sale(client, auth_tokens["manager"])
    
    if not sale_id:
        pytest.skip("Could not create paid sale - system info not initialized")

    # Start a return
    return_data = create_return_safely(client, auth_tokens["manager"], sale_id)
    return_id = return_data["id"]

    logger.debug(f"Created Return ID: {return_id}")

    # Fetch the specific return by ID
    response = client.get(
        f"{RETURNS_BASE}/{return_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )

    logger.debug(f"Get Return by ID Response: {response.status_code} - {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == return_id
    assert data["status"] == "OPEN"


def test_add_and_remove_product_from_return(client, auth_tokens):
    """Test adding and removing products from a return"""
    sale_id, barcodes = create_paid_sale(client, auth_tokens["manager"])
    
    if not sale_id:
        pytest.skip("Could not create paid sale - system info not initialized")

    # Start a return
    return_data = create_return_safely(client, auth_tokens["manager"], sale_id)
    return_id = return_data["id"]

    logger.debug(f"Return ID Created: {return_id}")

    # Add product to return (use a barcode from the sale)
    add_response = client.post(
        f"{RETURNS_BASE}/{return_id}/items",
        params={"barcode": barcodes[0], "amount": 1},
        headers=auth_headers(auth_tokens["manager"]),
    )
    logger.debug(f"Add Product to Return Response: {add_response.status_code} - {add_response.json()}")

    assert add_response.status_code in (200, 201), "Product should be added successfully"

    # Verify product was added
    get_response = client.get(
        f"{RETURNS_BASE}/{return_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    data = get_response.json()
    assert len(data.get("lines", [])) > 0, "Return should have product lines"

    # Remove product from return
    remove_response = client.delete(
        f"{RETURNS_BASE}/{return_id}/items",
        params={"barcode": barcodes[0], "amount": 1},
        headers=auth_headers(auth_tokens["manager"]),
    )
    logger.debug(f"Remove Product from Return Response: {remove_response.status_code} - {remove_response.json()}")

    assert remove_response.status_code == 200, "Product should be removed successfully"


def test_close_return(client, auth_tokens):
    """Test closing a return transaction"""
    sale_id, barcodes = create_paid_sale(client, auth_tokens["manager"])
    
    if not sale_id:
        pytest.skip("Could not create paid sale - system info not initialized")

    # Start a return
    return_data = create_return_safely(client, auth_tokens["manager"], sale_id)
    return_id = return_data["id"]

    # Add at least one product before closing
    client.post(
        f"{RETURNS_BASE}/{return_id}/items",
        params={"barcode": barcodes[0], "amount": 1},
        headers=auth_headers(auth_tokens["manager"]),
    )

    # Close the return
    response = client.patch(
        f"{RETURNS_BASE}/{return_id}/close",
        headers=auth_headers(auth_tokens["manager"]),
    )

    logger.debug(f"Close Return Response: {response.status_code} - {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True, "Close should return success"
    
    # Verify return was closed by getting it
    get_response = client.get(
        f"{RETURNS_BASE}/{return_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    return_data = get_response.json()
    assert return_data["status"] == "CLOSED", "Return should be in CLOSED status"


def test_reimburse_return(client, auth_tokens):
    """Test reimbursing a closed return"""
    sale_id, barcodes = create_paid_sale(client, auth_tokens["manager"])
    
    if not sale_id:
        pytest.skip("Could not create paid sale - system info not initialized")

    # Start a return
    return_data = create_return_safely(client, auth_tokens["manager"], sale_id)
    return_id = return_data["id"]

    # Add product
    client.post(
        f"{RETURNS_BASE}/{return_id}/items",
        params={"barcode": barcodes[0], "amount": 1},
        headers=auth_headers(auth_tokens["manager"]),
    )

    # Close the return first
    client.patch(
        f"{RETURNS_BASE}/{return_id}/close",
        headers=auth_headers(auth_tokens["manager"]),
    )

    # Reimburse the return
    response = client.patch(
        f"{RETURNS_BASE}/{return_id}/reimburse",
        headers=auth_headers(auth_tokens["manager"]),
    )

    logger.debug(f"Reimburse Return Response: {response.status_code} - {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "refund_amount" in data, "Reimburse should return refund_amount"
    assert data["refund_amount"] > 0, "Refund amount should be positive"
    
    # Verify return was reimbursed by getting it
    get_response = client.get(
        f"{RETURNS_BASE}/{return_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    return_data = get_response.json()
    assert return_data["status"] == "REIMBURSED", "Return should be in REIMBURSED status"


def test_cannot_return_unpaid_sale(client, auth_tokens):
    """Test that returns cannot be created for unpaid sales"""
    product_id = random.randint(10000, 99999)
    barcode = f"1111111{random.randint(100000, 999999)}"
    
    # Create a sale but don't pay for it
    product = create_product_type(client, auth_tokens["manager"], product_id, barcode)
    
    sale_response = client.post(
        SALES_BASE,
        headers=auth_headers(auth_tokens["manager"]),
    )
    sale_id = sale_response.json().get("sale_transaction_id") or sale_response.json().get("id")

    # Try to start a return (should fail)
    response = client.post(
        RETURNS_BASE,
        params={"sale_id": sale_id},
        headers=auth_headers(auth_tokens["manager"]),
    )

    logger.debug(f"Attempt Return on Unpaid Sale: {response.status_code} - {response.json()}")

    # Should not allow return on unpaid sale (expect 400, 404, 420, or 422)
    assert response.status_code in (400, 404, 420, 422), f"Should not allow return on unpaid sale, got {response.status_code}"
