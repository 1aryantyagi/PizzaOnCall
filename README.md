# PizzaOrder 🍕

PizzaOrder is a web and voice-based pizza ordering application that allows users to browse a menu, customize their orders, and place them seamlessly. The application supports both web-based interactions and voice-based ordering through Twilio.

## Features

- **Web Interface**: A user-friendly web interface for browsing the menu, managing the cart, and placing orders.
- **Voice Ordering**: Voice-based ordering powered by Twilio, allowing users to interact with the PizzaBot via phone calls.
- **Customizations**: Add toppings, choose crust types, and customize pizzas.
- **Cart Management**: Add, view, and delete items from the cart.
- **Payment Options**: Supports UPI and Cash on Delivery (COD) payment methods.
- **Order Management**: Logs orders in a PostgreSQL database and tracks delivery status.

## Project Structure

PizzaBot/
│── .gitignore
│── .env
│── Dockerfile
│── requirements.txt
│── product_catalog.json
│── README.md
│── static/                 # Static files (CSS, JS, images)
│   │── styles.css
│   │── script.js
│── templates/              # HTML templates for the frontend
│   │── index.html
│── audio_records/          # Folder for storing recorded audio files
│── tools.py                # Utility/helper functions
│── agent.py                # AI-powered PizzaAgent logic
│── app.py                  # Main Flask application
│── app1.py                 # Additional Flask app (consider merging if redundant)
│── test.py                 # Unit tests for the application

### Key Files

- **`app.py`**: Web-based interface for pizza ordering.
- **`app1.py`**: Voice-based interface using Twilio for handling phone calls.
- **`agent.py`**: Implements the PizzaBot using LangChain and OpenAI's GPT-3.5-turbo.
- **`tools.py`**: Contains utility classes for cart management, product catalog, payment processing, and order delivery.
- **`product_catalog.json`**: JSON file containing the menu items, customizations, and toppings.
- **`static/`**: Contains JavaScript and CSS files for the web interface.
- **`templates/`**: Contains the HTML template for the web interface.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/PizzaOrder.git
   cd PizzaOrder

2. Insrall dependencies:
   ```bash
   pip install -r requirements.txt
3. Set up environment variables: Create a .env file in the root directory with the following variables:
    ```bash
    OPENAI_API_KEY
    RAZORPAY_KEY_ID
    RENDER_DB_URL
    TWILIO_ACCOUNT
## Usage
1. Web Interface
  Start the flask application - app.py
2. Voice call
   Start the Flask application for voice ordering - app1.py
   Then configure Twilio to point to the /voice endpoint of your application.

## API Endpoints
### Web Endpoints
  GET /: Renders the web interface.
  POST /process_message: Processes user input and returns a response from the PizzaBot.
  GET /menu: Returns the menu items.
  GET /cart: Returns the current cart contents.
### Voice Endpoints
  POST /voice: Handles incoming voice calls.
  POST /handle_input: Processes user speech input and generates a response.
  
## Technologies Used
  Backend: Flask, LangChain, OpenAI GPT-3.5-turbo
  Frontend: HTML, CSS, JavaScript
  Database: PostgreSQL
  Payment Gateway: Razorpay
  Voice Integration: Twilio
  Containerization: Docker
  
## Acknowledgments
  OpenAI for GPT-3.5-turbo.
  Twilio for voice integration.
  Razorpay for payment processing.
