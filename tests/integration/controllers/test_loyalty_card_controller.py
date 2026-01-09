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


def generate_card_id():
    """Generate a random 10-digit card ID"""
    return f"{random.randint(1000000000, 9999999999)}"


def create_customer(client, token):
    """Helper function to create a customer for testing"""
    customer_id = random.randint(1000, 9999)
    
    response = client.post(
        CUSTOMERS_BASE,
        json={
            "id": customer_id,
            "name": f"Test Customer {customer_id}",
        },
        headers=auth_headers(token),
    )
    assert response.status_code in (200, 201), f"Failed to create customer: {response.text}"
    return response.json()


def create_loyalty_card(client, token, card_id=None, points=0):
    """Helper function to create a loyalty card"""
    if card_id is None:
        card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": points,
        },
        headers=auth_headers(token),
    )
    assert response.status_code in (200, 201), f"Failed to create loyalty card: {response.text}"
    return response.json()


# =====================================================================
# TESTS - Create Loyalty Card
# =====================================================================

def test_create_loyalty_card(client, auth_tokens):
    """Test creating a loyalty card"""
    card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 0,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["card_id"] == card_id
    assert data["points"] == 0


def test_create_loyalty_card_with_initial_points(client, auth_tokens):
    """Test creating a loyalty card with initial points"""
    card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 100,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["card_id"] == card_id
    assert data["points"] == 100


def test_create_loyalty_card_duplicate(client, auth_tokens):
    """Test that creating duplicate loyalty card fails"""
    card_id = generate_card_id()
    
    # Create first card
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 0,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 201
    
    # Try to create duplicate
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 0,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 409  # Conflict


def test_create_loyalty_card_invalid_length(client, auth_tokens):
    """Test that card ID with invalid length is rejected"""
    # Card ID too short
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": "123",
            "points": 0,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 422  # Validation error


def test_create_loyalty_card_negative_points(client, auth_tokens):
    """Test that negative initial points are rejected"""
    card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": -10,
        },
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 422  # Validation error


def test_create_loyalty_card_with_cashier(client, auth_tokens):
    """Test that cashier can create loyalty cards"""
    card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 0,
        },
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 201


def test_create_loyalty_card_with_admin(client, auth_tokens):
    """Test that admin can create loyalty cards"""
    card_id = generate_card_id()
    
    response = client.post(
        f"{CUSTOMERS_BASE}/cards",
        json={
            "card_id": card_id,
            "points": 0,
        },
        headers=auth_headers(auth_tokens["admin"]),
    )
    
    assert response.status_code == 201


# =====================================================================
# TESTS - Attach Card to Customer
# =====================================================================

def test_attach_card_to_customer(client, auth_tokens):
    """Test attaching loyalty card to customer"""
    # Create customer and card
    customer = create_customer(client, auth_tokens["manager"])
    card = create_loyalty_card(client, auth_tokens["manager"])
    
    # Attach card to customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    # Response is CustomerResponseDTO which should include the card info
    assert data["id"] == customer["id"]


def test_attach_card_with_zero_padding(client, auth_tokens):
    """Test that card ID is properly zero-padded when attaching"""
    customer = create_customer(client, auth_tokens["manager"])
    # Create card with specific ID
    card_id = "0000000123"
    card = create_loyalty_card(client, auth_tokens["manager"], card_id=card_id)
    
    # Attach using the numeric value (should be zero-padded)
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/123",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200


def test_attach_nonexistent_card(client, auth_tokens):
    """Test attaching non-existent card to customer returns 404"""
    customer = create_customer(client, auth_tokens["manager"])
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/9999999999",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_attach_card_to_nonexistent_customer(client, auth_tokens):
    """Test attaching card to non-existent customer returns 404"""
    card = create_loyalty_card(client, auth_tokens["manager"])
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/999999/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_attach_card_with_cashier(client, auth_tokens):
    """Test that cashier can attach cards"""
    customer = create_customer(client, auth_tokens["cashier"])
    card = create_loyalty_card(client, auth_tokens["cashier"])
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200


# =====================================================================
# TESTS - Modify Card Points
# =====================================================================

def test_add_points_to_card(client, auth_tokens):
    """Test adding points to loyalty card"""
    card = create_loyalty_card(client, auth_tokens["manager"], points=50)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 25},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["card_id"] == card["card_id"]
    assert data["points"] == 75  # 50 + 25


def test_subtract_points_from_card(client, auth_tokens):
    """Test subtracting points from loyalty card"""
    card = create_loyalty_card(client, auth_tokens["manager"], points=100)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": -30},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["points"] == 70  # 100 - 30


def test_subtract_points_below_zero(client, auth_tokens):
    """Test that subtracting more points than available results in 0"""
    card = create_loyalty_card(client, auth_tokens["manager"], points=50)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": -100},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["points"] == 0  # Floor at 0


def test_add_zero_points(client, auth_tokens):
    """Test adding zero points (no-op)"""
    card = create_loyalty_card(client, auth_tokens["manager"], points=50)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 0},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["points"] == 50  # Unchanged


def test_modify_points_nonexistent_card(client, auth_tokens):
    """Test modifying points for non-existent card returns 404"""
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/9999999999",
        params={"points": 10},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 404


def test_modify_points_with_zero_padding(client, auth_tokens):
    """Test that card ID is properly zero-padded when modifying points"""
    card_id = "0000000456"
    card = create_loyalty_card(client, auth_tokens["manager"], card_id=card_id, points=100)
    
    # Modify using numeric value (should be zero-padded)
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/456",
        params={"points": 50},
        headers=auth_headers(auth_tokens["manager"]),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["points"] == 150


def test_modify_points_with_cashier(client, auth_tokens):
    """Test that cashier can modify points"""
    card = create_loyalty_card(client, auth_tokens["cashier"], points=50)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 25},
        headers=auth_headers(auth_tokens["cashier"]),
    )
    
    assert response.status_code == 200
    assert response.json()["points"] == 75


def test_modify_points_with_admin(client, auth_tokens):
    """Test that admin can modify points"""
    card = create_loyalty_card(client, auth_tokens["admin"], points=50)
    
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 25},
        headers=auth_headers(auth_tokens["admin"]),
    )
    
    assert response.status_code == 200
    assert response.json()["points"] == 75


# =====================================================================
# TESTS - Combined Operations
# =====================================================================

def test_create_card_attach_and_add_points(client, auth_tokens):
    """Test complete workflow: create card, attach to customer, add points"""
    # Create customer and card
    customer = create_customer(client, auth_tokens["manager"])
    card = create_loyalty_card(client, auth_tokens["manager"], points=0)
    
    # Attach card
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    
    # Add points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 100},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 100
    
    # Add more points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 50},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 150


def test_multiple_point_modifications(client, auth_tokens):
    """Test multiple point modifications on same card"""
    card = create_loyalty_card(client, auth_tokens["manager"], points=100)
    
    # Add points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 50},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 150
    
    # Subtract points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": -30},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 120
    
    # Add more points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 80},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 200


def test_attach_same_card_to_different_customers(client, auth_tokens):
    """Test attaching the same card to different customers (should reassign)"""
    customer1 = create_customer(client, auth_tokens["manager"])
    customer2 = create_customer(client, auth_tokens["manager"])
    card = create_loyalty_card(client, auth_tokens["manager"])
    
    # Attach to first customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer1['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    
    # Attach same card to second customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer2['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200


def test_loyalty_card_lifecycle(client, auth_tokens):
    """Test complete loyalty card lifecycle"""
    # 1. Create customer
    customer = create_customer(client, auth_tokens["manager"])
    
    # 2. Create loyalty card with initial points
    card = create_loyalty_card(client, auth_tokens["manager"], points=10)
    assert card["points"] == 10
    
    # 3. Attach card to customer
    response = client.patch(
        f"{CUSTOMERS_BASE}/{customer['id']}/attach-card/{card['card_id']}",
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    
    # 4. Customer makes purchase - add points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 50},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 60
    
    # 5. Customer redeems points
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": -40},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 20
    
    # 6. Customer makes another purchase
    response = client.patch(
        f"{CUSTOMERS_BASE}/cards/{card['card_id']}",
        params={"points": 30},
        headers=auth_headers(auth_tokens["manager"]),
    )
    assert response.status_code == 200
    assert response.json()["points"] == 50
