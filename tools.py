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
    MENU_FILE = "product_catalog.json"

    @classmethod
    def load_menu(cls):
        """Loads the pizza menu from a JSON file."""
        try:
            with open(cls.MENU_FILE, "r", encoding="utf-8") as file:
                menu = json.load(file)
                if not isinstance(menu, list):
                    return None, "Error: Invalid menu format."
                return menu, None
        except (FileNotFoundError, json.JSONDecodeError):
            return None, "Error: Unable to load menu."

    @classmethod
    def search_pizza(cls, query: str) -> str:
        """Searches for a pizza based on a query."""
        menu, error = cls.load_menu()
        if error:
            return error
        
        query = query.lower()
        results = []
        
        for item in menu:
            name, description = item["name"].lower(), item["description"].lower()
            if query in name or query in description:
                score = 2
            else:
                score = max(
                    difflib.SequenceMatcher(None, query, name).ratio(),
                    difflib.SequenceMatcher(None, query, description).ratio()
                )
            if score > 0.4:
                results.append((score, f"🍕 **{item['name']}**\n- {item['description']}"))

        return "\n\n".join(res[1] for res in sorted(results, reverse=True, key=lambda x: x[0])) or "No matching pizzas found."
    
    @classmethod
    def list_all_pizzas(cls) -> str:
        """Lists all pizzas on the menu."""
        menu, error = cls.load_menu()
        if error:
            return error
        
        if not menu:
            return "No pizzas available."
        
        return "We have " + ", ".join(f"{i+1}- {item['name']}" for i, item in enumerate(menu)) + "."