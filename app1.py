from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
from agent import PizzaAgent
import os

load_dotenv()

app = Flask(__name__)
active_calls = {}

@app.route('/voice/incoming', methods=['POST'])
def handle_incoming_call():
    """Handle initial phone call connection"""
    call_sid = request.form.get('CallSid')
    caller_number = request.form.get('From')
    print(f"Incoming call from {caller_number} with SID {call_sid}")

    if not call_sid:
        return error_response("Invalid request.")

    active_calls[call_sid] = PizzaAgent()

    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/voice/handle-input',
        method='POST',
        speech_timeout=5,
        
    )
    gather.say("Welcome! I am your virtual pizza assistant. How can I assist you today?")
    response.append(gather)

    return Response(str(response), mimetype='text/xml')

@app.route('/voice/handle-input', methods=['POST'])
def handle_voice_input():
    """Process speech input and generate response"""
    call_sid = request.form.get('CallSid')
    speech_text = request.form.get('SpeechResult', '')

    agent = active_calls.get(call_sid)
    if not agent:
        return error_response("Session expired. Please call back.")

    try:
        text_response = agent.process_message(call_sid, speech_text)
        text_response = text_response.get('output', '')
    except Exception:
        return error_response("Error processing request.")

    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action='/voice/handle-input',
        method='POST',
        speech_timeout=5
    )
    gather.say(text_response)
    response.append(gather)

    return Response(str(response), mimetype='text/xml')

def error_response(message):
    """Create error response"""
    response = VoiceResponse()
    response.say(message)
    response.hangup()
    return Response(str(response), mimetype='text/xml')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)