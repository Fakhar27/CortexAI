"""
Example Google Cloud Function using Cortex
This shows how to use Cortex in a serverless environment
Directly based on production patterns
"""

from flask import jsonify
from cortex import Client
import os

# Initialize Cortex client (reused across invocations)
cortex_client = Client(db_path="/tmp/conversations.db")  # Use /tmp in cloud functions

# Mock coach data (in production, fetch from Firestore/database)
COACHES = {
    "fitness": {
        "name": "Mike",
        "instructions": "You are a fitness coach focused on exercise and nutrition",
        "personality": "Energetic and motivating"
    },
    "mindfulness": {
        "name": "Sarah",
        "instructions": "You are a mindfulness coach helping with meditation and stress",
        "personality": "Calm and peaceful"
    }
}


def coach_agent_endpoint(request):
    """
    Google Cloud Function endpoint for coach conversations
    
    Expected request body:
    {
        "coachId": "fitness",           // Which coach to use
        "pti": "resp_xxx",              // Previous response ID (optional)
        "message": "User's message"     // User input
    }
    """
    # CORS handling for browser requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for main request
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Parse request
        request_json = request.get_json()
        coach_id = request_json.get('coachId')
        pti = request_json.get('pti')  # Previous thread/response ID
        message = request_json.get('message')
        
        # Validate required fields
        if not coach_id or not message:
            return jsonify({
                "error": "Missing required fields",
                "details": "coachId and message are required"
            }), 400, headers
        
        # Get coach data
        coach = COACHES.get(coach_id)
        if not coach:
            return jsonify({
                "error": "Invalid coach",
                "details": f"Coach '{coach_id}' not found"
            }), 404, headers
        
        # Build parameters for Cortex (matches OpenAI Responses API)
        params = {
            "model": "cohere",  # or "gpt-4o" if using OpenAI
            "input": message,
            "store": True,
            "metadata": {
                "coach_id": coach_id,
                "function": "coach_agent"
            }
        }
        
        # Handle conversation continuity
        if pti:
            # Continue existing conversation
            params["previous_response_id"] = pti
            # Instructions are ignored when continuing (OpenAI spec)
        else:
            # New conversation - set coach instructions
            instructions = f"Your instructions as coach are: {coach['instructions']} and your personality is: {coach['personality']}"
            params["instructions"] = instructions
        
        # Call Cortex API (same interface as OpenAI)
        response = cortex_client.create(**params)
        
        # Handle errors
        if response.get("error"):
            return jsonify({
                "error": "AI service error",
                "details": response["error"]["message"]
            }), 500, headers
        
        # Extract response text
        assistant_reply = response["output"][0]["content"][0]["text"]
        
        # Return response (client saves response_id for next call)
        return jsonify({
            "responseId": response["id"],  # Client saves this as 'pti'
            "assistantReply": assistant_reply,
            "coachName": coach["name"]
        }), 200, headers
        
    except Exception as e:
        print(f"Error in coach_agent_endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500, headers


# For AWS Lambda
def lambda_handler(event, context):
    """AWS Lambda handler wrapper"""
    class FakeRequest:
        def __init__(self, body):
            self.method = 'POST'
            self._json = body
        
        def get_json(self):
            return self._json
    
    # Parse event body
    import json
    body = json.loads(event.get('body', '{}'))
    fake_request = FakeRequest(body)
    
    # Call the main function
    response = coach_agent_endpoint(fake_request)
    
    # Format for Lambda
    if isinstance(response, tuple):
        return {
            'statusCode': response[1],
            'headers': response[2] if len(response) > 2 else {},
            'body': json.dumps(response[0].json if hasattr(response[0], 'json') else response[0])
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(response.json if hasattr(response, 'json') else response)
        }


# For local testing
if __name__ == "__main__":
    """Test the function locally"""
    
    class MockRequest:
        def __init__(self, data):
            self.method = 'POST'
            self.data = data
        
        def get_json(self):
            return self.data
    
    print("Testing Cloud Function Locally\n")
    
    # Test 1: New conversation
    print("1. Starting new conversation with fitness coach:")
    request1 = MockRequest({
        "coachId": "fitness",
        "message": "I want to start working out"
    })
    
    # Create Flask app context for testing
    from flask import Flask
    app = Flask(__name__)
    with app.app_context():
        response1 = coach_agent_endpoint(request1)
        print(f"   Response: {response1[0].get_json()}")
    
    # Extract response_id for continuation
    response_id = response1[0].json["responseId"]
    
    # Test 2: Continue conversation
    print("\n2. Continuing conversation:")
    request2 = MockRequest({
        "coachId": "fitness",
        "pti": response_id,
        "message": "What exercises should I start with?"
    })
    response2 = coach_agent_endpoint(request2)
    print(f"   Response: {response2[0].json}")
    
    # Test 3: Different coach
    print("\n3. Starting conversation with mindfulness coach:")
    request3 = MockRequest({
        "coachId": "mindfulness",
        "message": "I'm feeling stressed"
    })
    response3 = coach_agent_endpoint(request3)
    print(f"   Response: {response3[0].json}")