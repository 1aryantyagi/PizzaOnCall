from flask import Flask, request, jsonify, render_template
from agent import PizzaAgent
import uuid
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

pizza_agent = PizzaAgent()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    session_id = data.get('session_id', str(uuid.uuid4()))
    message = data['message']
    
    response = pizza_agent.process_message(session_id, message)
    print(response)
    
    return jsonify({
        'response': response.get('output'),
        'session_id': session_id
    })

if __name__ == '__main__':
    app.run(debug=True)
