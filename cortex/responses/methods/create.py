"""Create method for Responses API - OpenAI compatible response generation"""
import uuid
import time
import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from cortex.models.registry import MODELS
from ..persistence import get_checkpointer, DatabaseError
from langgraph.graph import StateGraph, END
from ..state import ResponsesState

logger = logging.getLogger(__name__)


def _create_error_response(message: str, error_type: str = "api_error", param: Optional[str] = None, code: Optional[str] = None, response_id: Optional[str] = None) -> Dict[str, Any]:
    """Create an OpenAI-compatible error response with full structure
    
    Args:
        message: Error message
        error_type: Type of error
        param: Parameter that caused error
        code: Error code
        response_id: Response ID to include (for partial failures - allows conversation continuity)
    """
    error_obj = {
        "message": message,
        "type": error_type
    }
    
    if param:
        error_obj["param"] = param
    if code:
        error_obj["code"] = code
    
    return {
        "id": response_id,  
        "object": "response",
        "created_at": int(time.time()),
        "status": "failed",
        "error": error_obj,
        "incomplete_details": None,
        "instructions": None,
        "max_output_tokens": None,
        "model": None,
        "output": [],
        "parallel_tool_calls": None,
        "previous_response_id": None,
        "reasoning": None,
        "store": None,
        "temperature": None,
        "text": None,
        "tool_choice": None,
        "tools": None,
        "top_p": None,
        "truncation": None,
        "usage": None,
        "user": None,
        "metadata": None
    }


def _validate_create_inputs(input: str, model: str, temperature: float, metadata: Optional[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    """
    Validate inputs for create_response function
    
    Args:
        input: User's message
        model: LLM model name
        temperature: LLM temperature
        metadata: Optional metadata dict
        
    Returns:
        Error response dict if validation fails, None if valid
    """
    if not input:
        return _create_error_response(
            "Input cannot be empty",
            "invalid_request_error",
            "input",
            "missing_required_parameter"
        )
    
    if not isinstance(input, str):
        return _create_error_response(
            "Input must be a string",
            "invalid_request_error",
            "input",
            "invalid_type"
        )
    
    if not input.strip():
        return _create_error_response(
            "Input cannot be empty or whitespace only",
            "invalid_request_error",
            "input",
            "invalid_value"
        )
    
    if len(input) > 50000:
        return _create_error_response(
            f"Input too long. Maximum length is 50,000 characters, got {len(input)}",
            "invalid_request_error",
            "input",
            "invalid_value"
        )
    
    if not model or not isinstance(model, str):
        return _create_error_response(
            "Model must be a non-empty string",
            "invalid_request_error",
            "model",
            "invalid_value"
        )
    
    if model not in MODELS:
        available_models = list(MODELS.keys())
        return _create_error_response(
            f"Model '{model}' is not supported. Available models: {', '.join(available_models)}",
            "invalid_request_error",
            "model",
            "invalid_value"
        )
    
    if not isinstance(temperature, (int, float)):
        return _create_error_response(
            "Temperature must be a number",
            "invalid_request_error",
            "temperature",
            "invalid_type"
        )
    
    if temperature < 0 or temperature > 2.0:
        return _create_error_response(
            "Temperature must be between 0 and 2.0",
            "invalid_request_error",
            "temperature",
            "invalid_value"
        )
    
    if metadata is not None:
        if not isinstance(metadata, dict):
            return _create_error_response(
                "Metadata must be a dictionary",
                "invalid_request_error",
                "metadata",
                "invalid_type"
            )
        
        if len(str(metadata)) > 1000:
            return _create_error_response(
                "Metadata too large. Maximum size is 1000 characters",
                "invalid_request_error",
                "metadata",
                "invalid_value"
            )
    
    return None  


def create_response(
    api_instance,
    input: str,
    model: str,
    db_url: Optional[str] = None,
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
        db_url: Optional database URL for this request (overrides instance default)
        previous_response_id: Continue previous conversation
        instructions: System prompt (ignored if continuing conversation)
        store: Whether to persist conversation
        temperature: LLM temperature
        metadata: Custom key-value pairs
        
    Returns:
        OpenAI-compatible response dict or error
    """
    validation_error = _validate_create_inputs(input, model, temperature, metadata)
    if validation_error:
        logger.warning(f"Input validation failed: {validation_error['error']['message']}")
        return validation_error
    
    use_temp_graph = False
    temp_graph = None
    checkpointer_to_use = api_instance.checkpointer
    
    if db_url == "":
        db_url = None
    
    if db_url is not None and db_url != api_instance.db_url:
        
        try:
            logger.info(f"Creating temporary checkpointer for request-specific db_url")
            temp_checkpointer = get_checkpointer(db_url=db_url)
            checkpointer_to_use = temp_checkpointer
            
            workflow = StateGraph(ResponsesState)
            workflow.add_node("generate", api_instance._generate_node)
            workflow.set_entry_point("generate")
            workflow.add_edge("generate", END)
            temp_graph = workflow.compile(checkpointer=temp_checkpointer)
            use_temp_graph = True
            
        except DatabaseError as e:
            logger.error(f"Failed to create temporary checkpointer: {e}")
            return _create_error_response(
                str(e),
                "invalid_request_error",
                "db_url",
                "invalid_database_url"
            )
        except Exception as e:
            logger.error(f"Failed to create temporary graph: {e}")
            return _create_error_response(
                "Failed to connect to the specified database",
                "api_error",
                code="database_connection_error"
            )
    
    
    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    
    if previous_response_id:
        try:
            if not checkpointer_to_use.response_exists(previous_response_id):
                logger.info(f"Previous response not found: {previous_response_id}")
                return _create_error_response(
                    f"Response '{previous_response_id}' not found",
                    "invalid_request_error",
                    "previous_response_id",
                    "resource_not_found"
                )
            
            thread_id = checkpointer_to_use.get_thread_for_response(previous_response_id)
            if not thread_id:
                logger.warning(f"No thread_id found for response {previous_response_id}, using as thread_id")
                thread_id = previous_response_id
                
        except Exception as e:
            logger.error(f"Database error while checking previous response: {e}")
            return _create_error_response(
                "Database temporarily unavailable. Please try again.",
                "api_error",
                code="database_error"
            )
    else:
        thread_id = response_id
    
    messages = []
    if instructions and not previous_response_id:
        from langchain_core.messages import SystemMessage
        messages.append(SystemMessage(content=instructions))
    messages.append(HumanMessage(content=input))
    
    initial_state = {
        "messages": messages,  
        "response_id": response_id,
        "previous_response_id": previous_response_id,
        "input": input,
        "instructions": instructions if not previous_response_id else None,
        "model": model,
        "store": store,
        "temperature": temperature  
    }
    
    config = {
        "configurable": {
            "thread_id": thread_id,
            "response_id": response_id, 
            "store": store,  
            "checkpoint_ns": ""  
        }
    }
    
    if store and checkpointer_to_use:
        try:
            print(f"\n📝 PRE-EMPTIVE RESPONSE TRACKING")
            print(f"   Response ID: {response_id}")
            print(f"   Thread ID: {thread_id}")
            if hasattr(checkpointer_to_use, 'track_response'):
                checkpointer_to_use.track_response(response_id, thread_id, was_stored=False)
                print(f"   ✅ Response pre-registered for continuity")
        except Exception as track_error:
            print(f"   ⚠️ Pre-tracking failed (non-critical): {track_error}")
            pass
    
    max_retries = 2  
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            if retry_count > 0:
                print(f"\n🔄 RETRY ATTEMPT {retry_count}/{max_retries-1}")
                print(f"   Waiting 100ms before retry...")
                time.sleep(0.1)  
            
            graph_to_use = temp_graph if use_temp_graph else api_instance.graph
            
            logger.info(f"Invoking graph for response {response_id} with model {model} using {'temporary' if use_temp_graph else 'instance'} graph")
            result = graph_to_use.invoke(initial_state, config)
            
            if retry_count > 0:
                print(f"   ✅ Retry successful!")
            break
            
        except Exception as e:
            last_error = e
            error_message = str(e).lower()
            
            if "pipeline mode" in error_message or "pipeline" in error_message:
                retry_count += 1
                if retry_count < max_retries:
                    print(f"\n⚠️ Pipeline mode error detected - will retry")
                    logger.info(f"Pipeline error on attempt {retry_count}, retrying...")
                    continue  # Try again
                else:
                    print(f"\n❌ Pipeline error persists after {max_retries} attempts")
                    logger.error(f"Graph invocation failed after {max_retries} attempts: {str(e)}")
            else:
                logger.error(f"Graph invocation failed for response {response_id}: {str(e)}", exc_info=True)
                break
    
    if last_error:
        error_message = str(last_error).lower()
        
        if "pipeline mode" in error_message or "pipeline" in error_message:
            print(f"\n⚠️ PIPELINE MODE ERROR AFTER RETRIES - PRESERVING CONTINUITY")
            print(f"   🆔 Returning error WITH response_id: {response_id}")
            print(f"   📝 Conversation can continue from this point")
            return _create_error_response(
                "Database save partially failed after retries. The AI may have responded but checkpoint save failed. You can continue the conversation.",
                "api_error",
                code="pipeline_error",
                response_id=response_id  # CRITICAL: Include response_id for continuity
            )
        
        if any(keyword in error_message for keyword in ['network', 'connection', 'timeout', 'unreachable']):
            return _create_error_response(
                "AI service is temporarily unavailable due to network issues. Please try again in a moment.",
                "api_error",
                code="network_error"
            )
        
        if any(keyword in error_message for keyword in ['api key', 'api_key', 'co_api_key', 'authentication', 'unauthorized', 'forbidden', 'token', 'env']):
            return _create_error_response(
                "AI service authentication failed. Please check configuration.",
                "api_error",
                code="authentication_error"
            )
        
        if any(keyword in error_message for keyword in ['rate limit', 'quota', 'too many requests']):
            return _create_error_response(
                "AI service rate limit exceeded. Please try again later.",
                "api_error",
                code="rate_limit_exceeded"
            )
        if any(keyword in error_message for keyword in ['model', 'unavailable', 'not found']):
            return _create_error_response(
                f"Model '{model}' is temporarily unavailable. Please try a different model.",
                "invalid_request_error",
                "model",
                "model_unavailable"
            )
        
        return _create_error_response(
            "An unexpected error occurred while processing your request. Please try again.",
            "api_error",
            code="internal_error"
        )
    
    try:
        if not isinstance(result, dict):
            logger.error(f"Graph returned non-dict result: {type(result)}")
            return _create_error_response(
                "Invalid response format from AI service",
                "api_error",
                code="invalid_response"
            )
        
        all_messages = result.get("messages", [])
        if not all_messages:
            logger.error("Graph returned empty messages list")
            return _create_error_response(
                "No response generated from AI service",
                "api_error",
                code="empty_response"
            )
        
        ai_response = all_messages[-1]
        if not ai_response:
            logger.error("Last message in response is None/empty")
            return _create_error_response(
                "Empty response generated from AI service",
                "api_error",
                code="empty_response"
            )
        
        if not hasattr(ai_response, 'content'):
            logger.error(f"AI response missing content attribute: {type(ai_response)}")
            return _create_error_response(
                "Malformed response from AI service",
                "api_error",
                code="malformed_response"
            )
        
        content = ai_response.content
        if content is None:
            logger.warning("AI response content is None, using empty string")
            content = ""
        elif not isinstance(content, str):
            logger.warning(f"AI response content is not string: {type(content)}, converting")
            content = str(content)
            
    except Exception as e:
        logger.error(f"Error processing graph result: {e}", exc_info=True)
        return _create_error_response(
            "Failed to process AI response",
            "api_error",
            code="processing_error"
        )
    
    try:
        input_words = len(input.split()) if input else 0
        output_words = len(content.split()) if content else 0
        
        input_tokens = int(input_words * 1.3)
        output_tokens = int(output_words * 1.3)
        total_tokens = input_tokens + output_tokens
        
        message_id = f"msg_{uuid.uuid4().hex[:24]}"
        
        response = {
            "id": response_id,
            "object": "response",
            "created_at": int(time.time()),
            "status": "completed",
            "error": None,  # No error on success
            "incomplete_details": None,  # No incomplete details for successful response
            "instructions": instructions if not previous_response_id else None,  # Echo instructions (null if continuing)
            "max_output_tokens": None,  # Not implemented yet
            "model": model,
            "output": [{
                "type": "message",
                "id": message_id,  # Unique message ID
                "status": "completed",  # Message status
                "role": "assistant",
                "content": [{
                    "type": "output_text",
                    "text": content,
                    "annotations": []  # Empty annotations array
                }]
            }],
            "parallel_tool_calls": True,  # Default value
            "previous_response_id": previous_response_id,
            "reasoning": {  # Reasoning object (for o-series models)
                "effort": None,
                "summary": None
            },
            "store": store,
            "temperature": temperature,  # Echo back the temperature used
            "text": {  # Text format configuration
                "format": {
                    "type": "text"
                }
            },
            "tool_choice": "auto",  # Default tool choice
            "tools": [],  # Empty tools array (not implemented)
            "top_p": 1.0,  # Default top_p value
            "truncation": "disabled",  # Default truncation
            "usage": {
                "input_tokens": input_tokens,
                "input_tokens_details": {  # Token details
                    "cached_tokens": 0  # No caching implemented
                },
                "output_tokens": output_tokens,
                "output_tokens_details": {  # Output token details
                    "reasoning_tokens": 0  # No reasoning tokens
                },
                "total_tokens": total_tokens
            },
            "user": None  # No user tracking implemented
        }
        
    except Exception as e:
        logger.error(f"Error formatting response: {e}", exc_info=True)
        return _create_error_response(
            "Failed to format response",
            "api_error",
            code="formatting_error"
        )
    
    try:
        response["metadata"] = metadata if metadata is not None else {}
        
        logger.info(f"Successfully created response {response_id} with {total_tokens} tokens")
        return response
        
    except Exception as e:
        logger.error(f"Error in final response assembly: {e}", exc_info=True)
        return _create_error_response(
            "Failed to assemble final response",
            "api_error",
            code="assembly_error"
        )