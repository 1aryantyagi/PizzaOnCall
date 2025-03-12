from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
from tools import CartTool, PricingTool, PaymentTool, ProductTool

class PizzaAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        self.tools = [
            StructuredTool.from_function(
                func=lambda item, qty: CartTool.add_item("session_id_placeholder", item, qty),
                name="add_to_cart",
                description="Add items to the pizza order"
            ),
            StructuredTool.from_function(
                func=lambda: CartTool.get_cart("session_id_placeholder"),
                name="view_cart",
                description="View the current order contents"
            ),
            StructuredTool.from_function(
                func=lambda: PricingTool.calculate_total("session_id_placeholder"),
                name="calculate_total",
                description="Calculate the total order price"
            ),
            StructuredTool.from_function(
                func=lambda amt: PaymentTool.process_payment("session_id_placeholder", amt),
                name="process_payment",
                description="Process payment for the order"
            ),
            StructuredTool.from_function(
                func=lambda query: ProductTool.search_product(query),
                name="search_menu",
                description="Search pizza menu items by name or description. If the user asks for all pizza then list the pizzas"
            )
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a friendly and enthusiastic **Pizza Ordering Assistant**! 🍕
                Your goal is to **help customers order delicious pizzas**, customize them, and guide them through the checkout process.
                
                **Key Responsibilities:**
                - **Menu Assistance**: Help users find pizzas based on their preferences (e.g., cheesy, spicy, veggie).
                - **Customization**: Allow users to modify their order with extra toppings, crust types, or special instructions.
                - **Order Management**: Add items to the cart, view the cart, and modify orders.
                - **Pricing & Checkout**: Provide total pricing details and process payments securely.
                - **Delivery Information**: Confirm the order and provide an estimated delivery time.
                
                **Response Style:**
                - Be **cheerful, engaging, and helpful**.
                - Use **emoji-based expressions** to make interactions more fun.
                - Suggest add-ons like drinks, sides, and desserts to enhance their meal.
                - Ensure accuracy by confirming order details before proceeding to payment.
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
            "chat_history": self.chat_history  # Optionally, store history per session
        })
        self.chat_history.extend([
            ("human", user_input),
            ("ai", response["output"])
        ])
        return responsee