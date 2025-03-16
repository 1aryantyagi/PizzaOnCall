import os
import json
from tools import DeliveryTool
from dotenv import load_dotenv
load_dotenv()

def test_delivery_tool():
    print("Setting up database...")
    DeliveryTool.setup_database()

    # Test data
    session_id = "test_session_123"
    products = [{"id": 1, "name": "Laptop", "price": 1000}]
    user_details = {"name": "John Doe", "address": "123 Test Street"}
    payment_status = "paid"

    print("Logging test order...")
    order_id = DeliveryTool.log_order(session_id, products, user_details, payment_status)
    print(f"Order {order_id} logged successfully!")

    print("Fetching test order...")
    orders = DeliveryTool.get_orders(session_id)
    if orders:
        print("Retrieved Order:", json.dumps(orders, indent=4))
    else:
        print("No orders found!")

    print("Updating delivery status...")
    update_msg = DeliveryTool.update_delivery_status(order_id, "delivered")
    print(update_msg)

    print("Rechecking updated order...")
    updated_orders = DeliveryTool.get_orders(session_id)
    if updated_orders:
        print("Updated Order:", json.dumps(updated_orders, indent=4))
    else:
        print("No orders found after update!")

if __name__ == "__main__":
    test_delivery_tool()