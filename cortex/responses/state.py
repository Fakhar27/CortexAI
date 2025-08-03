"""State management for Responses API"""
from typing import TypedDict, List, Annotated, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ResponsesState(TypedDict):
    """State for managing conversations in Responses API
    
    This TypedDict defines the structure of data flowing through
    the LangGraph StateGraph for the Responses API.
    """
    # Core conversation messages (accumulated automatically)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Current response ID (generated for this turn)
    response_id: str
    
    # Previous response ID (links to conversation history)
    previous_response_id: Optional[str]
    
    # User's input message for this turn
    input: str
    
    # System instructions (personality/behavior)
    instructions: Optional[str]
    
    # Model to use (cohere, gpt-4, etc.)
    model: str
    
    # Whether to persist this conversation
    store: bool