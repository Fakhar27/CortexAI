"""Main ResponsesAPI class - orchestrates the Responses API functionality"""
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .state import ResponsesState
from .persistence import get_checkpointer
from .llm import get_llm
from .methods.create import create_response


class ResponsesAPI:
    """
    Main API class that replicates OpenAI's Responses API
    
    This class sets up the LangGraph workflow and provides
    methods for creating responses with conversation persistence.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the ResponsesAPI
        
        Args:
            db_path: Optional path to database for persistence
        """
        # Set up persistence
        self.checkpointer = get_checkpointer(db_path)
        
        # Set up the graph
        self.graph = self._setup_graph()
    
    def _setup_graph(self) -> StateGraph:
        """
        Set up the LangGraph workflow
        
        Returns:
            Compiled StateGraph with checkpointer
        """
        # Create workflow with our state schema
        workflow = StateGraph(ResponsesState)
        
        # Add the main node that generates responses
        workflow.add_node("generate", self._generate_node)
        
        # Set entry point
        workflow.set_entry_point("generate")
        
        # Add edge from generate to END
        workflow.add_edge("generate", END)
        
        # Compile with checkpointer for persistence
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _generate_node(self, state: ResponsesState) -> Dict[str, Any]:
        """
        Node that generates AI responses
        
        This is where the actual LLM call happens.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with AI response
        """
        # Get the LLM based on model in state
        llm = get_llm(state["model"])
        
        # Build messages for the LLM
        messages = []
        
        # Add system message if instructions provided
        if state.get("instructions"):
            messages.append(SystemMessage(content=state["instructions"]))
        
        # Add conversation history (already has user's new message)
        messages.extend(state["messages"])
        
        # Generate response
        ai_response = llm.invoke(messages)
        
        # Return updated state with AI response
        return {
            "messages": [ai_response]  # Will be added to existing messages
        }
    
    def create(
        self,
        input: str,
        model: str = "cohere",
        previous_response_id: Optional[str] = None,
        instructions: Optional[str] = None,
        store: bool = True,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a model response (main API method)
        
        Args:
            input: User's message
            model: LLM model to use
            previous_response_id: ID to continue previous conversation
            instructions: System instructions for the assistant
            store: Whether to persist the conversation
            temperature: LLM temperature setting
            metadata: Additional metadata to store
            
        Returns:
            OpenAI-compatible response dictionary
        """
        # Delegate to the create method
        return create_response(
            api_instance=self,
            input=input,
            model=model,
            previous_response_id=previous_response_id,
            instructions=instructions,
            store=store,
            temperature=temperature,
            metadata=metadata
        )