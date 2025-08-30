import os
import json
from cortex import Client

# Initialize client with environment variable
client = Client(db_url=os.getenv("DATABASE_URL"))

def lambda_handler(event, context):
    """
    Simple Lambda handler for Cortex API
    
    Expects API Gateway event with body containing:
    - input: User message (required)
    - model: LLM model to use (optional, default: "gpt-4o-mini")
    - previous_response_id: Continue conversation (optional)
    - instructions: System prompt (optional)
    - store: Whether to save conversation (optional, default: True)
    - temperature: LLM temperature (optional, default: 0.7)
    """
    try:
        # Handle both direct invocation and API Gateway events
        if isinstance(event.get("body"), str):
            # API Gateway event
            body = json.loads(event.get("body", "{}"))
        else:
            # Direct invocation
            body = event
        
        # Get required input
        user_input = body.get("input")
        if not user_input:
            raise ValueError("The 'input' parameter is required")

        # Call Cortex API
        response = client.create(
            input=user_input,
            model=body.get("model", "gpt-4o-mini"),
            previous_response_id=body.get("previous_response_id"),
            instructions=body.get("instructions"),
            store=body.get("store", True),
            temperature=body.get("temperature", 0.7)
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response)
        }

    except ValueError as e:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }