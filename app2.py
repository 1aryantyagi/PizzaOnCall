from flask import Flask, request, jsonify, Response, stream_with_context
from hashlib import sha256
from agent import PizzaAgent
import uuid
import json
import time

app = Flask(__name__)
pizza_agent = PizzaAgent()


def get_session_id(identifier: str) -> str:
    """
    Returns a hashed session ID based on the user identifier.
    """
    return sha256(identifier.encode()).hexdigest()


def generate_streaming_response(session_id: str, user_input: str):
    """
    Generator function to simulate streaming the agent's response as SSE events.
    """
    agent_response = pizza_agent.process_message(session_id, user_input)
    data = {"response": agent_response.get("output", "Sorry, could you say that again?"),
            "session_id": session_id}
    event = f"data: {json.dumps(data)}\n\n"
    yield event


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])
    streaming = data.get('stream', False)
    
    user_messages = [msg['content'] for msg in messages if msg.get('role') == 'user']
    user_input = user_messages[-1] if user_messages else "No user message found."

    user_identifier = data.get("phone", "anonymous")
    session_id = get_session_id(user_identifier)
    agent_response = pizza_agent.process_message(session_id, user_input)
    content = agent_response.get("output", "Sorry, could you say that again?")

    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    if streaming:
        def generate():
            for token in content.split():
                chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": "pizza-agent",
                    "choices": [{
                        "index": 0,
                        "delta": {"content": token + " "},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return Response(generate(), content_type='text/event-stream')
    
    else:
        response_data = {
            "id": response_id,
            "object": "chat.completion",
            "created": created,
            "model": "pizza-agent",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }]
        }
        return Response(json.dumps(response_data), content_type='application/json')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
