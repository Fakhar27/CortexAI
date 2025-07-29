"""Responses API implementation - OpenAI alternative"""
import uuid
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage
from .core.state import ConversationState
from .utils.llm import get_llm


class ResponsesAPI:
    """Simple API that replicates OpenAI's Responses API functionality"""
    
    def __init__(self, llm_provider: str = "cohere", db_path: str = ":memory:"):
        self.llm = get_llm(llm_provider)
        self.checkpointer = SqliteSaver.from_conn_string(db_path)
        self._setup_graph()
    
    def _setup_graph(self):
        """Setup the LangGraph workflow"""
        workflow = StateGraph(ConversationState)
        
        # Add response node
        workflow.add_node("respond", self._respond_node)
        
        # Set entry point
        workflow.set_entry_point("respond")
        
        # Add edge to END
        workflow.add_edge("respond", END)
        
        # Compile the graph
        self.app = workflow.compile(checkpointer=self.checkpointer)
    
    def _respond_node(self, state: ConversationState) -> Dict[str, Any]:
        """Node that generates responses"""
        # Use custom instructions if provided
        system_prompt = state.get("instructions", "You are a helpful assistant.")
        
        # Generate response
        response = self.llm.invoke([
            {"role": "system", "content": system_prompt},
            *state["messages"]
        ])
        
        return {"messages": [response]}
    
    def create(
        self,
        input: str,
        previous_response_id: Optional[str] = None,
        instructions: Optional[str] = None,
        store: bool = True
    ) -> Dict[str, Any]:
        """
        Create a response - matches OpenAI's Responses API
        
        Args:
            input: User message
            previous_response_id: ID of previous conversation to continue
            instructions: Custom instructions for the assistant
            store: Whether to persist the conversation
        
        Returns:
            Response with conversation_id and message
        """
        # Generate or use existing conversation ID
        conversation_id = previous_response_id or f"conv_{uuid.uuid4().hex[:12]}"
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=input)],
            "conversation_id": conversation_id,
            "instructions": instructions
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": conversation_id}} if store else {}
        result = self.app.invoke(initial_state, config)
        
        # Extract the response
        response_message = result["messages"][-1]
        
        return {
            "conversation_id": conversation_id,
            "message": {
                "role": "assistant",
                "content": response_message.content
            },
            "stored": store
        }