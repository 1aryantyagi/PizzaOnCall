import os
import random
import json
import difflib
import razorpay
from razorpay.errors import BadRequestError
import time
from dotenv import load_dotenv
load_dotenv()

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

        # Ensure base_part is a valid pizza
        if base_part not in CartTool.PIZZAS:
            return f"Error: '{base_part}' is not a valid pizza."

        base_product = CartTool.PRODUCTS[base_part]
        base_name = base_product["name"]

        # Validate modifiers
        valid_modifiers = []
        for mod in modifiers:
            mod_lower = mod.lower()
            
            # Fuzzy match against PRODUCTS (handling singular/plural naming)
            product_match = next(
                (p for p in CartTool.PRODUCTS.values() if mod_lower in p["name"].lower()), None
            )

            if not product_match:
                return f"Error: Modifier '{mod}' not found."
            
            # Ensure the modifier is a valid topping/customization
            if product_match["category"] not in ["topping", "customization"]:
                return f"Error: '{mod}' is not a valid topping or customization."
            
            valid_modifiers.append(product_match["name"])

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

class ProductTool:
    MENU_FILE = "product_catalog.json"
    _menu_cache = None

    @classmethod
    def load_menu(cls):
        """Loads the product menu from a JSON file if not already loaded."""
        if cls._menu_cache is None:
            try:
                with open(cls.MENU_FILE, "r", encoding="utf-8") as file:
                    menu = json.load(file)
                    if not isinstance(menu, list):
                        return None, "Error: Invalid menu format."
                    cls._menu_cache = menu  # Cache the menu after loading
            except (FileNotFoundError, json.JSONDecodeError):
                return None, "Error: Unable to load menu."
        
        return cls._menu_cache, None

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
        """Extracts available customizations from the cached menu."""
        menu, error = ProductTool.load_menu()
        if error:
            return None, error
        
        customizations = {"Cheese Options": [], "Toppings": []}

        for item in menu:
            if item.get("category") == "Cheese Options":
                customizations["Cheese Options"].append({
                    "name": item["name"],
                    "price": item["price"]
                })
            elif item.get("category") == "Toppings":
                customizations["Toppings"].append({
                    "name": item["name"],
                    "price": item["price"]
                })

        return customizations

    @staticmethod
    def list_customizations():
        customizations = ProductTool.get_customizations()
        result = []
        for category, items in customizations.items():
            result.append(f"{category}:")
            result.extend([f"- {item['name']} (₹{item['price']})" for item in items])
        return "\n".join(result)

# Work on this now
class PaymentTool:
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    @staticmethod
    def _get_cart_amount(session_id: str) -> tuple:
        """Helper to get cart amount and validate cart"""
        amount_str = CartTool.calculate_total(session_id)
        if "Error" in amount_str:
            return None, amount_str
            
        try:
            amount = float(amount_str.split("₹")[-1])
            return amount, None
        except (ValueError, IndexError):
            return None, "Error: Invalid total amount format"

    @staticmethod
    def process_payment(session_id: str, method: str, upi_id: str = None) -> str:
        """Process payment through Razorpay API. Supports UPI and COD both the methods."""
        # Validate cart and get amount
        amount, error = PaymentTool._get_cart_amount(session_id)
        if error:
            return error

        # Process payment method
        method = method.lower()
        if method == "upi":
            return PaymentTool._process_upi(session_id, amount, upi_id)
        elif method == "cod":
            return PaymentTool._process_cod(session_id, amount)
        else:
            return "Error: Invalid payment method. Choose 'UPI' or 'COD'"

    @staticmethod
    def _process_upi(session_id: str, amount: float, upi_id: str) -> str:
        """Handle UPI payment through Razorpay"""
        if not upi_id or '@' not in upi_id:
            return "Error: Invalid UPI ID format (should be xxx@bank)"

        client = razorpay.Client(auth=(PaymentTool.RAZORPAY_KEY_ID, 
                                    PaymentTool.RAZORPAY_KEY_SECRET))

        try:
            # Create payment order
            order = client.order.create({
                "amount": int(amount * 100),  # Convert to paisa
                "currency": "INR",
                "payment_capture": 1,
                "method": "upi"
            })
            print("ORDER RESPONSE:", order)

            # Monitor payment status (simplified)
            time.sleep(2)  # Simulate processing time
            payment = client.order.payments(order["id"])[0]

            if payment["status"] == "captured":
                CartTool.cart_data.pop(session_id, None)  # Clear cart
                return (f"✅ Payment successful! Transaction ID: {payment['id']}\n"
                        f"Amount: ₹{amount:.2f} | UPI: {upi_id}")
            
            return ("⚠️ Payment pending. Complete payment in your UPI app\n"
                    f"Order ID: {order['id']} | Amount: ₹{amount:.2f}")

        except BadRequestError as e:
            return f"❌ Payment failed: {str(e)}"
        except Exception as e:
            return f"Error processing payment: {str(e)}"

    @staticmethod
    def _process_cod(session_id: str, amount: float) -> str:
        """Handle Cash on Delivery"""
        CartTool.cart_data.pop(session_id, None)  # Clear cart
        return (f"🛒 COD Confirmed!\n"
                f"Amount: ₹{amount:.2f}\n"
                "Pay when you receive your order. Delivery time: 30-45 mins")


class DeliveryTool:
    @staticmethod
    def schedule_delivery(session_id: str):
        return {"eta": f"{random.randint(25, 45)} minutes", "status": "preparing"}