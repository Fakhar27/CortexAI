import os
import json
import time
from cortex import Client
try:
    from langchain_cohere import ChatCohere
    print("✅ ChatCohere imported successfully in Lambda")
    COHERE_AVAILABLE = True
except ImportError as e:
    print(f"❌ ChatCohere import failed in Lambda: {e}")
    COHERE_AVAILABLE = False

def lambda_handler(event, context):
    """
    Optimized Lambda handler for Cortex API
    
    Required parameters:
    - input: User message 
    
    Optional parameters:
    - db_url: Database connection string (falls back to MemorySaver if empty/missing)
    - model: LLM model (default: "gpt-4o-mini")
    - previous_response_id: Continue conversation
    - instructions: System prompt
    - store: Save conversation (default: True)
    - temperature: LLM temperature (default: 0.7)
    
    Returns complete response with timing and metadata
    """
    start_time = time.time()
    
    try:
        # Parse event body (handle both API Gateway and direct invocation)
        if isinstance(event.get("body"), str):
            # API Gateway event
            body = json.loads(event.get("body", "{}"))
        else:
            # Direct invocation
            body = event
        
        # Required parameters
        user_input = body.get("input")
        db_url = body.get("db_url")  # Can be empty string or None - persistence.py handles fallback
        
        if not user_input:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Missing required parameter: 'input'",
                    "required_fields": ["input"],
                    "optional_fields": ["db_url", "model", "previous_response_id", "instructions", "store", "temperature"]
                })
            }
        
        # Optional parameters with defaults
        model = body.get("model", "gpt-4o-mini")
        previous_response_id = body.get("previous_response_id")
        instructions = body.get("instructions") 
        store = body.get("store", True)
        temperature = body.get("temperature", 0.7)
        
        # Initialize client with provided db_url
        client = Client(db_url=db_url)
        
        # Build request parameters
        request_params = {
            "input": user_input,
            "model": model,
            "store": store,
            "temperature": temperature
        }
        
        # Add optional parameters if provided
        if previous_response_id:
            request_params["previous_response_id"] = previous_response_id
        if instructions:
            request_params["instructions"] = instructions
        
        # Call Cortex API
        response = client.create(**request_params)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Add timing and metadata to response
        response["execution_time"] = round(execution_time, 3)
        response["lambda_context"] = {
            "function_name": context.function_name if context else None,
            "memory_limit": context.memory_limit_in_mb if context else None,
            "request_id": context.aws_request_id if context else None
        }
        response["request_metadata"] = {
            "db_url_host": db_url.split("@")[1].split("/")[0] if db_url and "@" in db_url else ("local" if db_url else "memory"),
            "model_requested": model,
            "store_enabled": store,
            "has_previous_context": bool(previous_response_id),
            "has_instructions": bool(instructions)
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps(response)
        }

    except ValueError as e:
        # Client-side error (bad input)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e),
                "error_type": "validation_error",
                "execution_time": round(time.time() - start_time, 3)
            })
        }
    
    except Exception as e:
        # Server-side error
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": str(e),
                "error_type": "internal_error", 
                "execution_time": round(time.time() - start_time, 3),
                "context": {
                    "function_name": context.function_name if context else None,
                    "request_id": context.aws_request_id if context else None
                }
            })
        }