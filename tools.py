import random
import json
import difflib

import json

class CartTool:
    cart_data = {}  # Stores cart data per session
    PRICES = {}  # Stores price data for items
    PRICE_FILE = "product_catalog.json"  # File path for price data

    @staticmethod
    def add_item(session_id: str, item_name: str, quantity: int):
        """Adds an item to the cart after validating against the menu."""
        item_name = item_name.strip().lower()
        CartTool.load_prices_from_json(CartTool.PRICE_FILE)
        
        if item_name not in CartTool.PRICES:
            return f"Error: {item_name} is not in the menu."
        
        print(f"[DEBUG] Before adding: {CartTool.cart_data}")
        if session_id not in CartTool.cart_data:
            CartTool.cart_data[session_id] = {}
        
        CartTool.cart_data[session_id][item_name] = CartTool.cart_data[session_id].get(item_name, 0) + quantity
        print(f"[DEBUG] After adding {quantity} {item_name}: {CartTool.cart_data}")
        return f"Added {quantity} {item_name}(s)"

    @staticmethod
    def delete_item(session_id: str, item_name: str):
        """Deletes an item from the cart after validating against the menu."""
        item_name = item_name.strip().lower()
        CartTool.load_prices_from_json(CartTool.PRICE_FILE)
        
        if item_name not in CartTool.PRICES:
            return f"Error: {item_name} is not in the menu."
        
        print(f"[DEBUG] Before deleting: {CartTool.cart_data}")
        if session_id in CartTool.cart_data and item_name in CartTool.cart_data[session_id]:
            del CartTool.cart_data[session_id][item_name]
            print(f"[DEBUG] After deleting {item_name}: {CartTool.cart_data}")
            return f"Deleted {item_name} from the cart."
        
        print(f"[DEBUG] Delete failed: {item_name} not found in {session_id}'s cart.")
        return f"{item_name} not found in the cart."

    @staticmethod
    def get_cart(session_id: str):
        """Retrieves the cart items for a session."""
        print(f"[DEBUG] Fetching cart for session {session_id}: {CartTool.cart_data.get(session_id, {})}")
        items = CartTool.cart_data.get(session_id, {})
        return "Your cart is empty." if not items else "\n".join([f"{qty}x {name}" for name, qty in items.items()])

    @staticmethod
    def load_prices_from_json(file_path):
        """Loads prices from a JSON file into the PRICES dictionary."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                json_data = json.load(file)
            
            if not isinstance(json_data, list):
                print("[ERROR] Price data must be a list of dictionaries!")
                return
            
            CartTool.PRICES = {item["name"].strip().lower(): float(item["price"]) for item in json_data}
            print(f"[DEBUG] Prices loaded: {CartTool.PRICES}")
        
        except FileNotFoundError:
            print(f"[ERROR] File '{file_path}' not found!")
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON format in price file!")
        except (KeyError, ValueError) as e:
            print(f"[ERROR] Error processing price data: {e}")

    @staticmethod
    def calculate_total(session_id: str):
        """Calculates the total cost of the cart items."""
        CartTool.load_prices_from_json(CartTool.PRICE_FILE)
        cart_items = CartTool.cart_data.get(session_id, {})
        
        if not cart_items:
            return "Your cart is empty."
        
        total = sum(CartTool.PRICES.get(item, 0) * qty for item, qty in cart_items.items())
        return f"Total amount: ${total:.2f}"




class PaymentTool:
    @staticmethod
    def process_payment(session_id: str, amount: float):
        return "Payment processed successfully."


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
    def search_product(cls, query: str) -> str:
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