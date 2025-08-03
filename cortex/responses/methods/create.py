"""Create method for Responses API - OpenAI compatible response generation"""
import uuid
import time
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage


def create_response(
    api_instance,
    input: str,
    model: str = "cohere",
    previous_response_id: Optional[str] = None,
    instructions: Optional[str] = None,
    store: bool = True,
    temperature: float = 0.7,
    metadata: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create a model response (OpenAI-compatible)
    
    Args:
        api_instance: ResponsesAPI instance with graph
        input: User's message
        model: Which LLM to use
        previous_response_id: Continue previous conversation
        instructions: System prompt (ignored if continuing conversation)
        store: Whether to persist conversation
        temperature: LLM temperature
        metadata: Custom key-value pairs
        
    Returns:
        OpenAI-compatible response dict or error
    """
    # Step 1: ID Generation
    # Always generate a new response_id for this response
    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    
    # Step 2: Validate previous_response_id if provided
    if previous_response_id:
        # Check if the previous response exists in database
        if not api_instance.checkpointer.response_exists(previous_response_id):
            # Return OpenAI-compatible error
            return {
                "error": {
                    "message": f"Response '{previous_response_id}' not found",
                    "type": "invalid_request_error",
                    "param": "previous_response_id",
                    "code": "resource_not_found"
                }
            }
        
        # Get the thread_id that this response belongs to
        thread_id = api_instance.checkpointer.get_thread_for_response(previous_response_id)
        if not thread_id:
            # Fallback to using previous_response_id as thread_id
            # This handles old conversations before we added tracking
            thread_id = previous_response_id
    else:
        # New conversation - thread_id same as response_id
        thread_id = response_id
    
    # Step 3: State Preparation
    # Create initial state matching ResponsesState structure
    initial_state = {
        "messages": [HumanMessage(content=input)],  # Convert user input to message
        "response_id": response_id,
        "previous_response_id": previous_response_id,
        "input": input,
        "instructions": instructions,
        "model": model,
        "store": store
    }
    
    # Step 4: Graph Invocation with Smart Checkpointer
    # Configure with thread_id, store flag, AND response_id
    config = {
        "configurable": {
            "thread_id": thread_id,
            "response_id": response_id,  # Pass this so checkpointer can track it
            "store": store  # Pass store flag to SmartCheckpointer
        }
    }
    
    # Invoke the single graph with our state and config
    # The SmartCheckpointer will:
    # 1. Load previous messages if thread_id exists (get_tuple)
    # 2. Run through the graph nodes
    # 3. Track response_id -> thread_id mapping
    # 4. Save ONLY if store=True (put method checks this)
    result = api_instance.graph.invoke(initial_state, config)
    
    # Step 4: Response Formatting
    # Extract the AI's response from the result
    # The graph returns updated state with all messages
    all_messages = result["messages"]
    
    # Get the last message (AI's response)
    ai_response = all_messages[-1]
    
    # Format response to match OpenAI's structure
    response = {
        "id": response_id,
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "model": model,
        "output": [{
            "type": "message",
            "role": "assistant",
            "content": [{
                "type": "output_text",
                "text": ai_response.content
            }]
        }],
        "previous_response_id": previous_response_id,
        "store": store,
        "usage": {
            # Simple token estimation (1 word ≈ 1.3 tokens)
            "input_tokens": int(len(input.split()) * 1.3),
            "output_tokens": int(len(ai_response.content.split()) * 1.3),
            "total_tokens": int((len(input.split()) + len(ai_response.content.split())) * 1.3)
        }
    }
    
    # Add metadata if provided
    if metadata:
        response["metadata"] = metadata
    
    return response