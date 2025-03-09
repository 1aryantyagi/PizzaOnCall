import random
import json
import difflib

class CartTool:
    cart_data = {}  # Store cart items in memory

    @staticmethod
    def add_item(session_id: str, item_name: str, quantity: int):
        if session_id not in CartTool.cart_data:
            CartTool.cart_data[session_id] = {}
        
        CartTool.cart_data[session_id][item_name] = CartTool.cart_data[session_id].get(item_name, 0) + quantity
        return f"Added {quantity} {item_name}(s)"

    @staticmethod
    def get_cart(session_id: str):
        items = CartTool.cart_data.get(session_id, {})
        return "\n".join([f"{qty}x {name}" for name, qty in items.items()]) or "Empty"


class PricingTool:
    PRICES = {
        "large Margherita": 14.99,
        "extra cheese": 2.50,
        "Coke": 3.00,
        "garlic bread": 5.50
    }

    @staticmethod
    def calculate_total(session_id: str):
        cart_items = CartTool.cart_data.get(session_id, {})
        total = sum(PricingTool.PRICES.get(item, 0) * qty for item, qty in cart_items.items())
        return round(total, 2)


class PaymentTool:
    @staticmethod
    def process_payment(session_id: str, amount: float):
        return True  # Mock payment processing


class DeliveryTool:
    @staticmethod
    def schedule_delivery(session_id: str):
        return {"eta": f"{random.randint(25, 45)} minutes", "status": "preparing"}

class ProductTool:
    CATALOG_FILE = "product_catalog.json"

    @classmethod
    def load_catalog(cls):
        """Loads the product catalog from a JSON file and extracts the pizza list."""
        try:
            with open(cls.CATALOG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

                # Extract only the pizzas list
                if "pizzas" in data and isinstance(data["pizzas"], list):
                    cls.CATALOG = data["pizzas"]
                else:
                    cls.CATALOG = []  # Handle unexpected JSON format
                    print("Error: JSON file does not contain a valid pizzas list.")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            cls.CATALOG = []
            print(f"Error loading catalog: {e}")

    @classmethod
    def search_product(cls, query: str) -> str:
        """Search for a product with improved matching."""
        cls.load_catalog()
        query = query.lower()
        results = []
        
        for item in cls.CATALOG:
            name = item["name"].lower()
            description = item["description"].lower()
            
            if query in name or query in description:
                score = 2  # High score for direct match
            else:
                name_score = difflib.SequenceMatcher(None, query, name).ratio()
                desc_score = difflib.SequenceMatcher(None, query, description).ratio()
                score = max(name_score, desc_score)

            if score > 0.4:
                details = (
                    f"🍕 **{item['name']}**\n"
                    f"- {item['description']}\n"
                    f"- Sizes: {', '.join(item['sizes'].keys())}\n"
                    f"- Toppings: {', '.join(item['toppings'])}\n"
                    f"- Price: Small: ${item['sizes']['small']:.2f}, Medium: ${item['sizes']['medium']:.2f}, Large: ${item['sizes']['large']:.2f}"
                )
                results.append((score, details))

        results.sort(reverse=True, key=lambda x: x[0])
        return "\n\n".join([res[1] for res in results]) if results else "No matching items found"