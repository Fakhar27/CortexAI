"""State management for Responses API"""
from typing import TypedDict, List, Annotated, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ResponsesState(TypedDict):
    """State for managing conversations in Responses API
    
    This TypedDict defines the structure of data flowing through
    the LangGraph StateGraph for the Responses API.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    response_id: str
    previous_response_id: Optional[str]
    input: str
    instructions: Optional[str]
    model: str
    store: bool
    temperature: float