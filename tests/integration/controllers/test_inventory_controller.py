"""
Integration tests for Inventory Controller and Inventory Routes

Tests the inventory management functionality including:
- Updating product type quantity
- Updating product type position
- Error handling for invalid products
- Validation of quantity and position values
"""

import pytest
import random
from app.config.config import ROUTES

PRODUCTS_BASE = ROUTES["V1_PRODUCT_TYPES"]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def auth_headers(token: str):
    """Create authorization headers"""
    return {"Authorization": token}


def create_product(client, token, product_id: int = None):
    """Helper function to create a product type for testing"""
    if product_id is None:
        product_id = random.randint(10000, 99999)
    
    barcode = f"1234567{random.randint(100000, 999999)}"
    # Generate unique position for each product to avoid conflicts
    aisle = random.randint(1, 99)
    rack = random.randint(1, 99)
    level = random.randint(1, 99)
    position = f"{aisle}-{rack}-{level}"
    
    response = client.post(
        PRODUCTS_BASE,
        json={
            "id": product_id,
            "barcode": barcode,
            "description": f"Test Product {product_id}",
            "price_per_unit": 25.0,
            "quantity": 100,
            "position": position,
        },
        headers=auth_headers(token),
    )
    assert response.status_code in (200, 201), f"Failed to create product: {response.text}"
    return response.json()


# =====================================================================
# TESTS - Update Quantity
# =====================================================================

def test_update_product_quantity(client, auth_tokens):
    """Test updating product quantity"""
    # Create a product
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Update quantity
    new_quantity = 500
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": new_quantity},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["quantity"] == new_quantity


def test_update_product_quantity_to_zero(client, auth_tokens):
    """Test updating product quantity to zero"""
    # Create a product
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Update quantity to zero
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 0},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 0


def test_update_product_quantity_increase(client, auth_tokens):
    """Test increasing product quantity"""
    # Create a product with initial quantity
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    initial_quantity = product["quantity"]
    
    # Increase quantity
    new_quantity = initial_quantity + 200
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": new_quantity},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == new_quantity


def test_update_product_quantity_decrease(client, auth_tokens):
    """Test decreasing product quantity"""
    # Create a product with initial quantity
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    initial_quantity = product["quantity"]
    
    # Decrease quantity
    new_quantity = initial_quantity - 50
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": new_quantity},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == new_quantity


def test_update_quantity_invalid_product(client, auth_tokens):
    """Test updating quantity for non-existent product returns 404"""
    response = client.put(
        f"{PRODUCTS_BASE}/999999/quantity",
        json={"new_quantity": 100},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_update_quantity_negative_value(client, auth_tokens):
    """Test that negative quantity values are rejected"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": -10},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_update_quantity_requires_manager(client, auth_tokens):
    """Test that updating quantity requires manager or admin role"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Try with cashier token (should fail)
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 200},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    # Cashiers don't have permission for inventory management
    assert response.status_code == 403


def test_update_quantity_with_admin(client, auth_tokens):
    """Test that admin can also update quantity"""
    product = create_product(client, auth_tokens["admin"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 300},
        headers=auth_headers(auth_tokens["admin"]),
    )
    
    assert response.status_code == 200
    assert response.json()["quantity"] == 300


# =====================================================================
# TESTS - Update Position
# =====================================================================

def test_update_product_position(client, auth_tokens):
    """Test updating product position"""
    # Create a product
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Update position
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 2, "rackID": 3, "levelID": 4},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["position"] == "2-3-4"


def test_update_position_to_zeros(client, auth_tokens):
    """Test updating position to all zeros (valid edge case)"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 0, "rackID": 0, "levelID": 0},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == "0-0-0"


def test_update_position_large_numbers(client, auth_tokens):
    """Test updating position with large numbers"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 100, "rackID": 200, "levelID": 50},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == "100-200-50"


def test_update_position_invalid_product(client, auth_tokens):
    """Test updating position for non-existent product returns 404"""
    response = client.put(
        f"{PRODUCTS_BASE}/999999/position",
        json={"aisleID": 1, "rackID": 2, "levelID": 3},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_update_position_negative_aisle(client, auth_tokens):
    """Test that negative aisle values are rejected"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": -1, "rackID": 2, "levelID": 3},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_update_position_negative_rack(client, auth_tokens):
    """Test that negative rack values are rejected"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 1, "rackID": -2, "levelID": 3},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_update_position_negative_level(client, auth_tokens):
    """Test that negative level values are rejected"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 1, "rackID": 2, "levelID": -3},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    # Should return 422 for validation error
    assert response.status_code == 422


def test_update_position_requires_manager(client, auth_tokens):
    """Test that updating position requires manager or admin role"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Try with cashier token (should fail)
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 5, "rackID": 6, "levelID": 7},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    # Cashiers don't have permission for inventory management
    assert response.status_code == 403


def test_update_position_with_admin(client, auth_tokens):
    """Test that admin can also update position"""
    product = create_product(client, auth_tokens["admin"])
    product_id = product["id"]
    
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 10, "rackID": 20, "levelID": 30},
        headers=auth_headers(auth_tokens["admin"]),
    )
    
    assert response.status_code == 200
    assert response.json()["position"] == "10-20-30"


# =====================================================================
# TESTS - Combined Operations
# =====================================================================

def test_update_quantity_and_position(client, auth_tokens):
    """Test updating both quantity and position for same product"""
    # Create a product
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # Update quantity
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 250},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 250
    
    # Update position
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 3, "rackID": 4, "levelID": 5},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["position"] == "3-4-5"
    # Verify quantity is still correct
    assert data["quantity"] == 250


def test_multiple_quantity_updates(client, auth_tokens):
    """Test updating quantity multiple times"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # First update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 100},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 100
    
    # Second update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 200},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 200
    
    # Third update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 150},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 150


def test_multiple_position_updates(client, auth_tokens):
    """Test updating position multiple times"""
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    
    # First update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 1, "rackID": 2, "levelID": 3},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["position"] == "1-2-3"
    
    # Second update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 4, "rackID": 5, "levelID": 6},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["position"] == "4-5-6"
    
    # Third update
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 7, "rackID": 8, "levelID": 9},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["position"] == "7-8-9"


def test_full_inventory_management_workflow(client, auth_tokens):
    """Test complete inventory management workflow"""
    # 1. Create a product
    product = create_product(client, auth_tokens["manager"])
    product_id = product["id"]
    initial_position = product["position"]
    assert product["quantity"] == 100
    assert initial_position is not None  # Has some position
    
    # 2. Receive shipment - increase quantity
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 300},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 300
    
    # 3. Relocate product to new position
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/position",
        json={"aisleID": 5, "rackID": 10, "levelID": 2},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["position"] == "5-10-2"
    
    # 4. Simulate sales - decrease quantity
    response = client.put(
        f"{PRODUCTS_BASE}/{product_id}/quantity",
        json={"new_quantity": 250},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 250
    
    # 5. Verify final state
    response = client.get(
        f"{PRODUCTS_BASE}/{product_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 250
    assert data["position"] == "5-10-2"
