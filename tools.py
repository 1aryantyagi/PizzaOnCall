import random
import json
import difflib


class CartTool:
    cart_data = {}  # Stores carts by session ID
    PRODUCTS = {}    # Product data loaded from JSON (key: lowercase name)
    PIZZAS = {}      # Pizza products
    CUSTOMIZATIONS = {}  # Customization products
    TOPPINGS = {}    # Topping products
    PRICE_FILE = "product_catalog.json"

    @classmethod
    def load_products(cls):
        """Load product data from JSON file and categorize them, but only if empty."""
        if cls.PRODUCTS:
            return
        
        try:
            with open(cls.PRICE_FILE, "r") as f:
                products = json.load(f)
                cls.PRODUCTS.clear()
                for item in products:
                    key = item["name"].strip().lower()
                    cls.PRODUCTS[key] = {
                        "name": item["name"],
                        "price": item["price"],
                        "category": item["category"]
                    }
                # Create category-specific lookups
                cls.PIZZAS = {k: v for k, v in cls.PRODUCTS.items() if v["category"] == "pizza"}
                cls.CUSTOMIZATIONS = {k: v for k, v in cls.PRODUCTS.items() if v["category"] == "customization"}
                cls.TOPPINGS = {k: v for k, v in cls.PRODUCTS.items() if v["category"] == "topping"}
        except Exception as e:
            print(f"Error loading products: {e}")

    @staticmethod
    def add_item(session_id: str, item_name: str, quantity: int):
        """Adds an item to the cart with proper parsing of pizza, customizations, and toppings."""
        CartTool.load_products()  # Ensure data is loaded
        item_name = item_name.strip().lower()
        
        # Split into base pizza and modifiers
        parts = item_name.split(" with ")
        base_part = parts[0].strip()
        modifiers = []
        if len(parts) > 1:
            modifiers = [m.strip() for m in parts[1].split(" and ")]
        
        # Validate base pizza
        if base_part not in CartTool.PIZZAS:
            return f"Error: Pizza '{base_part}' not found."
        base_product = CartTool.PRODUCTS[base_part]
        base_name = base_product["name"]
        
        # Validate modifiers
        valid_modifiers = []
        for mod in modifiers:
            mod_lower = mod.lower()
            
            # Match against normalizing keys
            product_match = next((p for p in CartTool.PRODUCTS.values() if p["name"].lower() == mod_lower), None)
            
            if product_match:
                valid_modifiers.append(product_match["name"])
            else:
                return f"Error: Modifier '{mod}' not found."
        
        # Update cart
        cart = CartTool.cart_data.setdefault(session_id, {})
        cart[base_name] = cart.get(base_name, 0) + quantity
        for mod in valid_modifiers:
            cart[mod] = cart.get(mod, 0) + quantity
        
        # Build response
        response = f"Added {quantity} {base_name}"
        if valid_modifiers:
            response += f" with {', '.join(valid_modifiers)}"
        return response + "."


    @staticmethod
    def delete_item(session_id: str, item_name: str):
        """Removes an item from the cart with case-insensitive lookup."""
        CartTool.load_products()
        item_lower = item_name.strip().lower()
        product = CartTool.PRODUCTS.get(item_lower)
        if not product:
            return f"Error: {item_name} not in menu."
        original_name = product["name"]
        
        if session_id in CartTool.cart_data and original_name in CartTool.cart_data[session_id]:
            del CartTool.cart_data[session_id][original_name]
            return f"Removed {original_name} from cart."
        return f"{original_name} not found in cart."

    @staticmethod
    def get_cart(session_id: str):
        """Retrieves formatted cart contents."""
        items = CartTool.cart_data.get(session_id, {})
        if not items:
            return "Your cart is empty."
        return "\n".join([f"{qty}x {item}" for item, qty in items.items()])

    @staticmethod
    def calculate_total(session_id: str):
        """Calculates the total price of items in the cart."""
        total = 0.0
        cart = CartTool.cart_data.get(session_id, {})
        for item, qty in cart.items():
            product = CartTool.PRODUCTS.get(item.lower())
            if product:
                total += product["price"] * qty
        return f"Total: ₹{total:.2f}"

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

        pizzas = [item["name"] for item in menu if item.get("category") == "pizza"]

        if not pizzas:
            return "No pizzas available."

        return "We have " + ", ".join(f"{i+1}- {name}" for i, name in enumerate(pizzas)) + "."


    @staticmethod
    def get_customizations():
        return {
            "Cheese Options": [
                {"name": "Cheese Burst", "price": 150},
                {"name": "Cheese Blanket", "price": 250}
            ],
            "Toppings": [
                {"name": "Paneer Topping", "price": 80},
                {"name": "Jalapeno Topping", "price": 80}
            ]
        }

    @staticmethod
    def list_customizations():
        customizations = ProductTool.get_customizations()
        result = []
        for category, items in customizations.items():
            result.append(f"{category}:")
            result.extend([f"- {item['name']} (₹{item['price']})" for item in items])
        return "\n".join(result)