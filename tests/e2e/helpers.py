"""
E2E Test Helpers and Utilities

These helpers create complete, realistic test data for end-to-end scenarios.
"""
import random
import string


def generate_barcode(prefix="E2E"):
    """Generate a unique 12-digit numeric barcode for e2e tests."""
    # Generate a 12-digit numeric barcode (valid UPC-A format)
    return ''.join(random.choices(string.digits, k=12))


def generate_customer_name():
    """Generate a random customer name."""
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_loyalty_card():
    """Generate a random loyalty card number."""
    return ''.join(random.choices(string.digits, k=10))


def create_product_helper(client, token, name, price, quantity=100):
    """Create a complete product with random barcode and position."""
    barcode = generate_barcode()
    product_id = random.randint(10000, 99999)
    # Use much larger ranges to avoid position conflicts
    position = f"{random.randint(1, 100)}-{random.choice('ABCDEFGHIJ')}-{random.randint(1, 1000)}"
    
    response = client.post(
        "http://127.0.0.1:8000/api/v1/products",  # Changed from /product-types
        json={
            "id": product_id,
            "barcode": barcode,
            "description": name,  # Use name as description
            "price_per_unit": price,
            "quantity": quantity,
            "position": position,
        },
        headers={"Authorization": token}
    )
    
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create product: {response.status_code} - {response.text}")
    
    # Normalize response
    data = response.json()
    if "id" in data and "product_type_id" not in data:
        data["product_type_id"] = data["id"]
    return data


def create_customer_helper(client, token, name=None):
    """Create a customer."""
    if name is None:
        name = generate_customer_name()
    
    response = client.post(
        "http://127.0.0.1:8000/api/v1/customers",
        json={"name": name},
        headers={"Authorization": token}
    )
    
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create customer: {response.text}")
    
    # Response uses "id" not "customer_id"
    data = response.json()
    # Normalize the response to include customer_id field for consistency
    if "id" in data and "customer_id" not in data:
        data["customer_id"] = data["id"]
    return data


def attach_loyalty_card_helper(client, token, customer_id, card_number=None):
    """Attach a loyalty card to a customer."""
    if card_number is None:
        card_number = generate_loyalty_card()
    
    # First create the card
    card_response = client.post(
        "http://127.0.0.1:8000/api/v1/customers/cards",
        json={"card_id": card_number, "points": 0},
        headers={"Authorization": token}
    )
    
    if card_response.status_code not in (200, 201):
        raise Exception(f"Failed to create loyalty card: {card_response.text}")
    
    # Then attach it using the correct endpoint
    attach_response = client.patch(
        f"http://127.0.0.1:8000/api/v1/customers/{customer_id}/attach-card/{card_number}",
        headers={"Authorization": token}
    )
    
    if attach_response.status_code not in (200, 201):
        raise Exception(f"Failed to attach loyalty card: {attach_response.text}")
    
    # Normalize card response
    card_data = card_response.json()
    if "card_id" in card_data and "card_number" not in card_data:
        card_data["card_number"] = card_data["card_id"]
    return card_data


def complete_sale_helper(client, cashier_token, products_to_sell):
    """
    Complete a full sale workflow.
    
    Args:
        client: TestClient
        cashier_token: Authorization token
        products_to_sell: List of tuples [(product, quantity), ...]
    
    Returns:
        Sale transaction data
    """
    # Start sale
    start_response = client.post(
        "http://127.0.0.1:8000/api/v1/sales",
        headers={"Authorization": cashier_token}
    )
    assert start_response.status_code == 201
    sale = start_response.json()
    sale_id = sale.get("sale_transaction_id") or sale.get("id")
    
    # Add products
    for product, quantity in products_to_sell:
        add_response = client.post(
            f"http://127.0.0.1:8000/api/v1/sales/{sale_id}/items",
            params={"barcode": product["barcode"], "amount": quantity},
            headers={"Authorization": cashier_token}
        )
        assert add_response.status_code == 201
    
    # Close sale
    close_response = client.patch(
        f"http://127.0.0.1:8000/api/v1/sales/{sale_id}/close",
        headers={"Authorization": cashier_token}
    )
    assert close_response.status_code == 200
    
    # Get updated sale to compute total cost from lines
    get_response = client.get(
        f"http://127.0.0.1:8000/api/v1/sales/{sale_id}",
        headers={"Authorization": cashier_token}
    )
    assert get_response.status_code == 200
    sale = get_response.json()
    
    # Compute total cost from sale lines (cost field is 0 until paid)
    total_cost = 0.0
    for line in sale.get("lines", []):
        line_total = line["unit_price"] * line["quantity"] * (1 - line.get("discount_rate", 0))
        total_cost += line_total
    total_cost *= (1 - sale.get("discount_rate", 0))
    
    # Pay for sale
    pay_response = client.patch(
        f"http://127.0.0.1:8000/api/v1/sales/{sale_id}/pay",
        params={"cash_amount": total_cost + 10},
        headers={"Authorization": cashier_token}
    )
    assert pay_response.status_code == 200
    
    # Get final sale with updated cost
    final_response = client.get(
        f"http://127.0.0.1:8000/api/v1/sales/{sale_id}",
        headers={"Authorization": cashier_token}
    )
    return final_response.json()
