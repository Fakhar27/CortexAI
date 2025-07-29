"""State management for conversations"""
from typing import TypedDict, List, Annotated, Optional
from langchain_core.messages import BaseMessage, add_messages


class ConversationState(TypedDict):
    """State for managing conversations"""
    messages: Annotated[List[BaseMessage], add_messages]
    conversation_id: str
    active_agent: Optional[str]
    instructions: Optional[str]