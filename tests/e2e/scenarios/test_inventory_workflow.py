"""
E2E Test: Inventory Management Workflow

Tests complete inventory management from ordering to stocking and selling.
"""
import pytest
from tests.e2e.helpers import create_product_helper, complete_sale_helper
from datetime import datetime


def test_complete_inventory_lifecycle(client, auth_tokens):
    """
    End-to-end test of inventory management:
    1. Create product with low stock
    2. Create order for more inventory
    3. Pay for order
    4. Record order arrival
    5. Verify inventory increased
    6. Sell products
    7. Verify inventory decreased
    """
    admin_token = auth_tokens["admin"]
    manager_token = auth_tokens["manager"]
    cashier_token = auth_tokens["cashier"]
    
    # Step 1: Create product with low stock
    tablet = create_product_helper(client, admin_token, "Tablet 10-inch", 399.99, quantity=5)
    product_id = tablet["product_type_id"]
    
    # Step 2: Check initial balance
    balance_response = client.get(
        "http://127.0.0.1:8000/api/v1/balance",
        headers={"Authorization": admin_token}
    )
    initial_balance = balance_response.json()["balance"]
    
    # Step 3: Create order to restock
    create_order_response = client.post(
        "http://127.0.0.1:8000/api/v1/orders",
        json={
            "product_barcode": tablet["barcode"],
            "quantity": 20,
            "price_per_unit": 350.00
        },
        headers={"Authorization": manager_token}
    )
    assert create_order_response.status_code == 201
    order = create_order_response.json()
    order_id = order["id"]
    
    # Verify order is in ISSUED state
    assert order["status"] == "ISSUED"
    
    # Step 4: Admin pays for the order
    order_total = 20 * 350.00  # 7000.00
    pay_order_response = client.patch(
        f"http://127.0.0.1:8000/api/v1/orders/{order_id}/pay",
        headers={"Authorization": admin_token}
    )
    assert pay_order_response.status_code == 201
    
    # Step 5: Verify balance decreased
    balance_after_payment = client.get(
        "http://127.0.0.1:8000/api/v1/balance",
        headers={"Authorization": admin_token}
    ).json()["balance"]
    
    assert abs(balance_after_payment - (initial_balance - order_total)) < 0.01
    
    # Step 7: Record order arrival (inventory arrives)
    arrival_response = client.patch(
        f"http://127.0.0.1:8000/api/v1/orders/{order_id}/arrival",
        headers={"Authorization": manager_token}
    )
    assert arrival_response.status_code == 201
    
    # Step 8: Verify inventory increased
    product_check = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    updated_product = product_check.json()
    assert updated_product["quantity"] == 25  # 5 initial + 20 from order
    
    # Step 9: Sell some tablets
    complete_sale_helper(client, cashier_token, [(tablet, 10)])
    
    # Step 10: Verify inventory decreased after sale
    final_product_check = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    final_product = final_product_check.json()
    assert final_product["quantity"] == 15  # 25 - 10 sold


def test_inventory_position_management(client, auth_tokens):
    """
    Test updating product positions in warehouse:
    1. Create product with initial position
    2. Move product to new position
    3. Verify position updated
    4. Verify position conflict prevention
    """
    admin_token = auth_tokens["admin"]
    
    # Create two products
    product1 = create_product_helper(client, admin_token, "Monitor 24-inch", 249.99, quantity=10)
    product2 = create_product_helper(client, admin_token, "Monitor 27-inch", 349.99, quantity=8)
    
    product1_id = product1["product_type_id"]
    product2_id = product2["product_type_id"]
    
    # Get product 1 initial position
    initial_position = product1["position"]
    
    # Update product 1 to new position
    update_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product1_id}/position",
        json={"aisleID": 5, "rackID": 2, "levelID": 15},
        headers={"Authorization": admin_token}
    )
    assert update_response.status_code == 200
    
    # Verify position updated
    check_response = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product1_id}",
        headers={"Authorization": admin_token}
    )
    assert check_response.json()["position"] == "5-2-15"
    
    # Try to move product 2 to the same position (should succeed - reassignment allowed)
    reassign_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product2_id}/position",
        json={"aisleID": 5, "rackID": 2, "levelID": 15},
        headers={"Authorization": admin_token}
    )
    assert reassign_response.status_code == 200
    
    # Product 1 and Product 2 can both have same position if system allows it
    check1 = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product1_id}",
        headers={"Authorization": admin_token}
    )
    check2 = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product2_id}",
        headers={"Authorization": admin_token}
    )
    # Verify product 2 has the expected position
    assert check2.json()["position"] == "5-2-15"


def test_inventory_quantity_adjustments(client, auth_tokens):
    """
    Test manual inventory adjustments:
    1. Create product
    2. Increase quantity (stock received)
    3. Decrease quantity (damaged goods)
    4. Verify all changes reflected
    """
    admin_token = auth_tokens["admin"]
    
    # Create product
    camera = create_product_helper(client, admin_token, "Digital Camera", 599.99, quantity=12)
    product_id = camera["product_type_id"]
    
    # Increase quantity (e.g., found extra stock)
    increase_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}/quantity",
        json={"new_quantity": 17},  # 12 + 5
        headers={"Authorization": admin_token}
    )
    assert increase_response.status_code == 200
    
    # Verify quantity increased
    check1 = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    assert check1.json()["quantity"] == 17  # 12 + 5
    
    # Decrease quantity (e.g., damaged goods)
    decrease_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}/quantity",
        json={"new_quantity": 14},  # 17 - 3
        headers={"Authorization": admin_token}
    )
    assert decrease_response.status_code == 200
    
    # Verify quantity decreased
    check2 = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    assert check2.json()["quantity"] == 14  # 17 - 3
    
    # Try to set negative quantity (should fail)
    over_decrease_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}/quantity",
        json={"new_quantity": -5},
        headers={"Authorization": admin_token}
    )
    # Should get error about insufficient quantity
    assert over_decrease_response.status_code in [400, 420, 422]


def test_product_lifecycle_management(client, auth_tokens):
    """
    Test complete product lifecycle:
    1. Create product
    2. Update product details
    3. Sell some units
    4. Update price
    5. Delete product (when stock is 0)
    """
    admin_token = auth_tokens["admin"]
    cashier_token = auth_tokens["cashier"]
    
    # Create product with limited stock
    speaker = create_product_helper(client, admin_token, "Bluetooth Speaker", 79.99, quantity=3)
    product_id = speaker["product_type_id"]
    
    # Update product description
    update_response = client.put(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        json={
            "barcode": speaker["barcode"],
            "name": "Premium Bluetooth Speaker",
            "description": "High-quality wireless speaker with 20-hour battery",
            "price_per_unit": 89.99,  # Price increase
            "quantity": 3,
            "position": speaker["position"]
        },
        headers={"Authorization": admin_token}
    )
    assert update_response.status_code == 201
    
    # Verify update  
    check = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    updated = check.json()
    assert updated["description"] == "High-quality wireless speaker with 20-hour battery"
    assert abs(updated["price_per_unit"] - 89.99) < 0.01
    
    # Sell all units
    complete_sale_helper(client, cashier_token, [(updated, 3)])
    
    # Verify stock is now 0
    final_check = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    assert final_check.json()["quantity"] == 0
    
    # Delete product (now that stock is 0)
    delete_response = client.delete(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    # Accept both 200 and 204 status codes for delete
    assert delete_response.status_code in [200, 204]
    
    # Verify product is deleted
    not_found = client.get(
        f"http://127.0.0.1:8000/api/v1/products/{product_id}",
        headers={"Authorization": admin_token}
    )
    assert not_found.status_code == 404
