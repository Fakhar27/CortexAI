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
        OpenAI-compatible response dict
    """
    # Step 1: ID Generation
    # Always generate a new response_id for this response
    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    
    # Determine thread_id for conversation continuity
    if previous_response_id:
        # Continuing existing conversation
        thread_id = previous_response_id
    else:
        # New conversation - thread_id same as response_id
        thread_id = response_id
    
    # Step 2: State Preparation
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
    
    # Handle previous conversation loading for store=False
    # If user wants to continue a conversation but not save the new response
    if not store and previous_response_id:
        # We need to manually load the previous conversation
        # Since ephemeral graph won't have access to it
        # TODO: Implement conversation retrieval from SQLite
        # For now, just warn the user
        print(f"Warning: store=False with previous_response_id may not load history properly")
    
    # Step 3: Graph Invocation
    # Choose the right graph and config based on store parameter
    if store:
        # Use persistent graph with thread_id for conversation continuity
        config = {"configurable": {"thread_id": thread_id}}
        graph = api_instance.persistent_graph
    else:
        # Use ephemeral graph - no persistence, no thread_id needed
        config = {}
        graph = api_instance.ephemeral_graph
    
    # Invoke the appropriate graph with our state and config
    # This is where the magic happens - LangGraph handles:
    # 1. Loading previous messages (if thread_id exists and store=True)
    # 2. Running through the graph nodes
    # 3. Saving the result (only if store=True)
    result = graph.invoke(initial_state, config)
    
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