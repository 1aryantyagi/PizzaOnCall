from flask import Flask, render_template, request, jsonify, session
import uuid
from agent import PizzaAgent
from tools import ProductTool, CartTool
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'pizza_secret_123'

pizza_agent = PizzaAgent()

@app.route('/')
def index():
    # Generate session ID if not exists
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/process_message', methods=['POST'])
def process_message():
    data = request.json
    user_input = data.get('message')
    session_id = session['session_id']
    
    response = pizza_agent.process_message(session_id, user_input)
    return jsonify({
        'response': response['output'],
        'session_id': session_id
    })

@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify({
        'pizzas': ProductTool.list_all_pizzas(),
        'customizations': ProductTool.list_customizations()
    })

@app.route('/cart', methods=['GET'])
def get_cart():
    session_id = session['session_id']
    return jsonify({
        'items': CartTool.get_cart(session_id),
        'total': CartTool.calculate_total(session_id)
    })

if __name__ == '__main__':
    app.run(debug=True)