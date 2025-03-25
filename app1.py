from flask import Flask, render_template, request, jsonify, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import uuid
from agent import PizzaAgent
from tools import ProductTool, CartTool
from dotenv import load_dotenv
import os
from hashlib import sha256

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'pizza_secret_123')

pizza_agent = PizzaAgent()

def get_session_id(phone_number):
    """Generate consistent session ID from phone number"""
    return sha256(phone_number.encode()).hexdigest()

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    """Handle incoming voice calls"""
    caller_number = request.form.get('From')
    print(f"Incoming call from: {caller_number}")

    response = VoiceResponse()
    
    gather = Gather(
        input='speech',
        action='/handle_input',
        method='POST',
        speechTimeout='auto'
    )
    gather.say("Welcome to PizzaBot! What would you like to order today?")
    response.append(gather)
    
    response.redirect('/voice')
    return str(response)

@app.route('/handle_input', methods=['POST'])
def handle_input():
    """Process user speech input and generate response"""
    response = VoiceResponse()
    session_id = get_session_id(request.form.get('From', ''))
    
    user_input = request.form.get('SpeechResult', '')
    print(f"User input: {user_input}")
    agent_response = pizza_agent.process_message(session_id, user_input)
    
    gather = Gather(
        input='speech',
        action='/handle_input',
        method='POST',
        speechTimeout='auto'
    )

    gather.say(agent_response.get('output', 'Sorry, I didn\'t get that. Can you please repeat?'))
    response.append(gather)

    response.redirect('/voice')
    return str(response)

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

if __name__ == '__main__':
    app.run(debug=True)