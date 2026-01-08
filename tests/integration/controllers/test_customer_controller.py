"""
Integration tests for Customer Controller and Customer Routes

Tests the full customer management workflow including:
- Creating customers
- Listing and searching customers
- Getting customer by ID
- Updating customer information
- Deleting customers
- Creating loyalty cards
- Attaching loyalty cards to customers
- Modifying card points
"""

import pytest
import random
from app.config.config import ROUTES

CUSTOMERS_BASE = ROUTES["V1_CUSTOMERS"]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def auth_headers(token: str):
    """Create authorization headers"""
    return {"Authorization": token}


def create_customer(client, token, name: str):
    """Helper function to create a customer"""
    response = client.post(
        CUSTOMERS_BASE,
        json={"name": name},
        headers=auth_headers(token),
    )
    assert response.status_code == 201, f"Failed to create customer: {response.text}"
    return response.json()


def create_loyalty_card(client, token, card_id: str, points: int = 0):
    """Helper function to create a loyalty card"""
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={"card_id": card_id, "points": points},
        headers=auth_headers(token),
    )
    assert response.status_code == 201, f"Failed to create loyalty card: {response.text}"
    return response.json()


# =====================================================================
# TESTS
# =====================================================================

def test_create_customer(client, auth_tokens):
    """Test creating a new customer"""
    customer_name = f"Test Customer {random.randint(1000, 9999)}"
    
    response = client.post(
        CUSTOMERS_BASE,
        json={"name": customer_name},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == customer_name
    assert "id" in data
    # Card field may be absent or None when no loyalty card is attached
    assert data.get("card") is None or data.get("loyalty_card") is None


def test_create_customer_duplicate_name(client, auth_tokens):
    """Test that creating a customer with duplicate name fails"""
    customer_name = f"Duplicate Customer {random.randint(1000, 9999)}"
    
    # Create first customer
    create_customer(client, auth_tokens["cashier"], customer_name)
    
    # Try to create another with same name
    response = client.post(
        CUSTOMERS_BASE,
        json={"name": customer_name},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 409  # Conflict


def test_list_customers(client, auth_tokens):
    """Test listing all customers"""
    # Create a few customers
    create_customer(client, auth_tokens["cashier"], f"Customer A {random.randint(1000, 9999)}")
    create_customer(client, auth_tokens["cashier"], f"Customer B {random.randint(1000, 9999)}")
    
    response = client.get(
        CUSTOMERS_BASE,
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_customer_by_id(client, auth_tokens):
    """Test getting a customer by ID"""
    customer_name = f"Test Customer {random.randint(1000, 9999)}"
    created = create_customer(client, auth_tokens["cashier"], customer_name)
    customer_id = created["id"]
    
    response = client.get(
        f"{CUSTOMERS_BASE}/{customer_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == customer_name


def test_get_customer_not_found(client, auth_tokens):
    """Test getting a non-existent customer returns 404"""
    response = client.get(
        f"{CUSTOMERS_BASE}/999999",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 404


def test_update_customer_name(client, auth_tokens):
    """Test updating a customer's name"""
    customer_name = f"Original Name {random.randint(1000, 9999)}"
    created = create_customer(client, auth_tokens["cashier"], customer_name)
    customer_id = created["id"]
    
    new_name = f"Updated Name {random.randint(1000, 9999)}"
    response = client.put(
        f"{CUSTOMERS_BASE}/{customer_id}",
        json={"name": new_name},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == new_name


def test_update_customer_not_found(client, auth_tokens):
    """Test updating a non-existent customer returns 404"""
    response = client.put(
        f"{CUSTOMERS_BASE}/999999",
        json={"name": "New Name"},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 404


def test_delete_customer(client, auth_tokens):
    """Test deleting a customer"""
    customer_name = f"To Delete {random.randint(1000, 9999)}"
    created = create_customer(client, auth_tokens["cashier"], customer_name)
    customer_id = created["id"]
    
    response = client.delete(
        f"{CUSTOMERS_BASE}/{customer_id}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 204
    
    # Verify customer is deleted
    get_response = client.get(
        f"{CUSTOMERS_BASE}/{customer_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    assert get_response.status_code == 404


def test_delete_customer_not_found(client, auth_tokens):
    """Test deleting a non-existent customer returns 404"""
    response = client.delete(
        f"{CUSTOMERS_BASE}/999999",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_create_loyalty_card(client, auth_tokens):
    """Test creating a loyalty card"""
    card_id = f"{random.randint(1000000000, 9999999999)}"
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={"card_id": card_id, "points": 100},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["card_id"] == card_id.zfill(10)
    assert data["points"] == 100


def test_create_loyalty_card_duplicate(client, auth_tokens):
    """Test that creating a duplicate loyalty card fails"""
    card_id = f"{random.randint(1000000000, 9999999999)}"
    
    # Create first card
    create_loyalty_card(client, auth_tokens["cashier"], card_id, 50)
    
    # Try to create another with same card_id
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={"card_id": card_id, "points": 100},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 409  # Conflict


def test_attach_loyalty_card_to_customer(client, auth_tokens):
    """Test attaching a loyalty card to a customer"""
    # Create customer
    customer_name = f"Customer with Card {random.randint(1000, 9999)}"
    customer = create_customer(client, auth_tokens["cashier"], customer_name)
    customer_id = customer["id"]
    
    # Create loyalty card
    card_id = f"{random.randint(1000000000, 9999999999)}"
    card = create_loyalty_card(client, auth_tokens["cashier"], card_id, 50)
    
    # Attach card to customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer_id}/attach-card/{card_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    # Card can be under 'card' or 'loyalty_card' key
    card_data = data.get("card") or data.get("loyalty_card")
    assert card_data is not None
    assert card_data["card_id"] == card_id.zfill(10)
    assert card_data["points"] == 50


def test_attach_card_customer_not_found(client, auth_tokens):
    """Test attaching a card to non-existent customer returns 404"""
    card_id = f"{random.randint(1000000000, 9999999999)}"
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/999999/attach-card/{card_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 404


def test_attach_card_not_found(client, auth_tokens):
    """Test attaching a non-existent card returns 404"""
    customer = create_customer(client, auth_tokens["cashier"], f"Customer {random.randint(1000, 9999)}")
    customer_id = customer["id"]
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer_id}/attach-card/9999999999",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 404


def test_modify_card_points(client, auth_tokens):
    """Test modifying loyalty card points"""
    # Create card
    card_id = f"{random.randint(1000000000, 9999999999)}"
    card = create_loyalty_card(client, auth_tokens["cashier"], card_id, 100)
    
    # Add points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card_id}",
        params={"points": 50},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["card_id"] == card_id.zfill(10)
    assert data["points"] == 150  # 100 + 50


def test_modify_card_points_negative(client, auth_tokens):
    """Test subtracting loyalty card points"""
    # Create card with points
    card_id = f"{random.randint(1000000000, 9999999999)}"
    card = create_loyalty_card(client, auth_tokens["cashier"], card_id, 100)
    
    # Subtract points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card_id}",
        params={"points": -30},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["points"] == 70  # 100 - 30


def test_modify_card_not_found(client, auth_tokens):
    """Test modifying a non-existent card returns 404"""
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/9999999999",
        params={"points": 50},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 404


def test_full_customer_workflow(client, auth_tokens):
    """Test complete customer workflow with loyalty card"""
    # 1. Create customer
    customer_name = f"Workflow Customer {random.randint(1000, 9999)}"
    customer = create_customer(client, auth_tokens["cashier"], customer_name)
    customer_id = customer["id"]
    
    # 2. Create loyalty card
    card_id = f"{random.randint(1000000000, 9999999999)}"
    card = create_loyalty_card(client, auth_tokens["cashier"], card_id, 0)
    
    # 3. Attach card to customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer_id}/attach-card/{card_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    assert response.status_code == 200
    
    # 4. Add points to card
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card_id}",
        params={"points": 100},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 100
    
    # 5. Update customer name
    new_name = f"Updated Workflow {random.randint(1000, 9999)}"
    response = client.put(
        f"{CUSTOMERS_BASE}/{customer_id}",
        json={"name": new_name},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    card_data = data.get("card") or data.get("loyalty_card")
    assert card_data["points"] == 100
    
    # 6. Verify customer with card
    response = client.get(
        f"{CUSTOMERS_BASE}/{customer_id}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name
    card_data = data.get("card") or data.get("loyalty_card")
    assert card_data["card_id"] == card_id.zfill(10)
    assert card_data["points"] == 100
