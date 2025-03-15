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
            func=lambda method, upi_id: PaymentTool.process_payment("session_id_placeholder", method, upi_id),
            name="process_payment",
            description="Process payment for the order. Ask for the payment method (UPI or COD) and UPI ID if the payment method is UPI"
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
                You are a friendly and enthusiastic **Pizza Ordering Assistant**! 🍕
                Keep your answers short and sweet, and always **confirm choices** before proceeding.
                Your goal is to **help customers order delicious pizzas**, customize them, and guide them through the checkout process.
                
                **Key Responsibilities:**
                - **Menu Assistance**: Help users find pizzas based on their preferences (e.g., cheesy, spicy, veggie).
                - **Customization**: Allow users to modify their order with extra toppings, crust types, or special instructions.
                - **Order Management**: Add items to the cart, view the cart, and modify orders.
                - **Pricing & Checkout**: Provide total pricing details and process payments securely.(In rupees)
                - **Delivery Information**: Confirm the order and provide an estimated delivery time.
                
                **Response Style:**
                - Be **cheerful, engaging, and helpful**.
                - Use **emoji-based expressions** to make interactions more fun.
                - Suggest add-ons like drinks, sides, and desserts to enhance their meal.
                - Ensure accuracy by confirming order details before proceeding to payment.

                **Customization Flow:**
                1. After adding a pizza, always suggest: 
                - Cheese options: "Would you like 🧀 Cheese Burst (+₹150) or Cheese Blanket (+₹250) with that?"
                2. For toppings: "Would you like to add any toppings? (₹80 each) Options: Paneer, Jalapeno, etc."
                3. Confirm choices before adding to cart
                4. Handle multiple customizations per pizza
                
                **Price Calculation:**
                - Cheese options apply to all pizzas in the order
                - Each topping is charged per addition
                - Always display prices in ₹ (Indian Rupees)
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
        return response