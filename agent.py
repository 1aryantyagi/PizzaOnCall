from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
from tools import CartTool, PaymentTool, ProductTool

class PizzaAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        self.tools = [
            StructuredTool.from_function(
                func=lambda item, qty: CartTool.add_item("session_id_placeholder", item, qty),
                name="add_to_cart",
                description="Add items to the pizza order"
            ),
            StructuredTool.from_function(
                func=lambda item, qty: CartTool.delete_item("session_id_placeholder", item),
                name="delete_from_cart",
                description="Deletes the item from the cart"
            ),
            StructuredTool.from_function(
                func=lambda: CartTool.get_cart("session_id_placeholder"),
                name="view_cart",
                description="View the current order contents"
            ),
            StructuredTool.from_function(
                func=lambda: CartTool.calculate_total("session_id_placeholder"),
                name="calculate_total",
                description="Calculate the total order price"
            ),
            StructuredTool.from_function(
            func=lambda method, name, address, phone, upi_id: PaymentTool.process_payment("session_id_placeholder", method, name, address, phone, upi_id),
            name="process_payment",
            description="Process payment for the order. Ask for the payment method (UPI or COD) and UPI ID if the payment method is UPI, Then ask for the name, address, and phone number of the customer."
            ),
            StructuredTool.from_function(
                func=lambda query: ProductTool.search_product(query),
                name="search_menu",
                description="Search pizza menu items by name or description."
            ),
            StructuredTool.from_function(
                func=lambda: ProductTool.list_all_pizzas(),
                name="load_menu",
                description="List all the pizzas available in the menu"
            ),
            StructuredTool.from_function(
                func=lambda: ProductTool.list_customizations(),
                name="Search_customization",
                description="Load the customization options for the pizzas"
            ),

        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
            """
                You are Pizza Assistant, a voice-based AI that helps customers order delicious pizzas. You assist with menu selection, customization, order management, pricing, and checkout.

                **Key Responsibilities:**
                - Menu Assistance: Help users choose pizzas based on their preferences (cheesy, spicy, veggie, etc.).
                - Customization: Allow users to modify orders with extra toppings, crust types, or special instructions.
                - Order Management: Add items to the cart, view the cart, and modify orders.
                - Pricing & Checkout: Provide total pricing in rupees and process payments securely.
                - Delivery Information: Confirm orders and provide an estimated delivery time.
                
                Response Style:
                - Be clear, concise, and professional.
                - Ensure accuracy by confirming order details before proceeding.
                - If the input is unclear, ask the user to repeat it.


                Customization Flow:
                1- After selecting a pizza, ask:
                  "Would you like Cheese Burst (+₹150) or Cheese Blanket (+₹250) with that?"
                2- For toppings:
                  "Would you like to add any toppings? (₹80 each) Options: Paneer, Jalapeno, etc."
                3- Confirm choices before adding to the cart.


                Price Calculation:
                - Cheese options apply to all pizzas in the order.
                - Each topping is charged per addition.
                - Always display prices in ₹ (Indian Rupees).
                
                Checkout & Payment Flow:
                1- Ask for delivery details:
                    Name: "Can I get your name for the order?"
                    Address: "Where should we deliver your pizza?"
                    Phone Number: "Please provide your contact number for updates."
                    Payment Method: "Would you like to pay via UPI or Cash on Delivery?"
                2- Confirm the entire order, total price, and estimated delivery time before processing the payment.
                3- Once confirmed, provide UPI payment details and finalize the order.
            """),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])

        self.agent = create_openai_tools_agent(
            self.llm, self.tools, self.prompt
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True
        )
        self.chat_history = []

    def process_message(self, session_id: str, user_input: str) -> str:
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history
        })
        self.chat_history.extend([
            ("human", user_input),
            ("ai", response["output"])
        ])
        print("INSIDE AGENT", response)
        return response