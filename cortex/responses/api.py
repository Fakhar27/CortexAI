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
        try:
            # Validate db_path if provided
            if db_path is not None:
                import os
                # Check if parent directory exists
                parent_dir = os.path.dirname(db_path)
                if parent_dir and not os.path.exists(parent_dir):
                    raise ValueError(f"Database directory does not exist: {parent_dir}")
            
            # Initialize checkpointer with error handling
            try:
                self.checkpointer = get_checkpointer(db_path)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize database: {str(e)}")
            
            # Setup graph with error handling
            try:
                self.graph = self._setup_graph()
            except Exception as e:
                raise RuntimeError(f"Failed to setup graph workflow: {str(e)}")
                
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"ResponsesAPI initialization failed: {str(e)}")
    
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
        try:
            # Get the LLM based on model in state, with user's temperature
            # Extract temperature from initial request (passed through state)
            temperature = state.get("temperature")
            llm = get_llm(state["model"], temperature=temperature)
            
            # Build messages for the LLM
            messages = []
            
            # Add system message if instructions provided
            if state.get("instructions"):
                messages.append(SystemMessage(content=state["instructions"]))
            
            # Add conversation history (already has user's new message)
            messages.extend(state["messages"])
            
            # Generate response with error handling
            try:
                ai_response = llm.invoke(messages)
            except Exception as e:
                # LLM invocation failed - create error message
                error_msg = str(e).lower()
                
                # Check for specific error types
                if any(keyword in error_msg for keyword in ['api_key', 'api key', 'authentication', 'unauthorized']):
                    error_content = "Authentication failed. Please check your API key configuration."
                elif any(keyword in error_msg for keyword in ['rate', 'limit', 'quota', 'too many']):
                    error_content = "Rate limit exceeded. Please wait a moment and try again."
                elif any(keyword in error_msg for keyword in ['timeout', 'timed out']):
                    error_content = "Request timed out. The AI service is taking too long to respond."
                elif any(keyword in error_msg for keyword in ['context', 'length', 'too long', 'token']):
                    error_content = "Message too long. Please reduce the length of your input."
                else:
                    error_content = f"AI service error: {str(e)}"
                
                # Create an error response message
                ai_response = AIMessage(content=f"Error: {error_content}")
            
            # Return updated state with AI response
            return {
                "messages": [ai_response]  # Will be added to existing messages
            }
            
        except Exception as e:
            # Catch any other unexpected errors
            # Return an error message instead of crashing
            return {
                "messages": [AIMessage(content=f"System error: {str(e)}")]
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