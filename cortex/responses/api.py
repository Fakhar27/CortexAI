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
    
    def __init__(self, db_url: Optional[str] = None, db_path: Optional[str] = None):
        """
        Initialize the ResponsesAPI
        
        Args:
            db_url: PostgreSQL connection string for production/serverless.
                   Can also be set via DATABASE_URL environment variable.
                   Format: postgresql://user:pass@host:port/database
            db_path: [DEPRECATED] Legacy parameter for SQLite path.
                    Use db_url for PostgreSQL or leave empty for SQLite.
        """
        try:
            import os
            from .persistence import DatabaseError
            
            # Handle legacy db_path parameter
            if db_path is not None:
                import warnings
                warnings.warn(
                    "db_path parameter is deprecated. "
                    "Use db_url for PostgreSQL or leave empty for local SQLite.",
                    DeprecationWarning,
                    stacklevel=2
                )
                # For backwards compatibility, treat db_path as SQLite
                if db_url is None:
                    # Validate db_path if provided
                    parent_dir = os.path.dirname(db_path)
                    if parent_dir and not os.path.exists(parent_dir):
                        raise ValueError(f"Database directory does not exist: {parent_dir}")
            
            # Initialize checkpointer with error handling
            try:
                self.checkpointer = get_checkpointer(db_url=db_url)
                self.db_url = db_url
            except DatabaseError as e:
                # Re-raise database errors with original message
                raise e
            except Exception as e:
                raise RuntimeError(f"Failed to initialize database: {str(e)}")
            
            # Setup graph with error handling
            try:
                self.graph = self._setup_graph()
            except Exception as e:
                raise RuntimeError(f"Failed to setup graph workflow: {str(e)}")
                
        except DatabaseError:
            # Let DatabaseError pass through unchanged
            raise
        except Exception as e:
            # Re-raise with more context for other errors
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
            print(f"\n🧠 LLM GENERATION NODE")
            print(f"   Model: {state.get('model')}")
            print(f"   Temperature: {state.get('temperature', 0.7)}")
            print(f"   Messages in state: {len(state.get('messages', []))}")
            
            # Get the LLM based on model in state, with user's temperature
            # Extract temperature from initial request (passed through state)
            temperature = state.get("temperature")
            llm = get_llm(state["model"], temperature=temperature)
            
            # Build messages for the LLM
            # FIXED: Don't add system message here - it's already in state["messages"] from checkpoint
            # The system message was added during initial state creation and persists through checkpoints
            messages = list(state["messages"])  # Use messages directly from state (includes system message)
            
            # Check if we have instructions (for logging only)
            has_system_msg = any(isinstance(msg, SystemMessage) for msg in messages)
            if has_system_msg:
                print(f"   Instructions: Yes (from checkpoint)")
            elif state.get("instructions"):
                print(f"   Instructions: Yes (but not in messages - this is a bug!)")
            print(f"   Total messages to LLM: {len(messages)}")
            
            # Show conversation preview
            if len(messages) > 1:
                print(f"   📜 Conversation history:")
                for i, msg in enumerate(messages[-3:]):  # Show last 3 messages
                    role = msg.__class__.__name__.replace("Message", "")
                    content_preview = str(msg.content)[:80] if hasattr(msg, 'content') else str(msg)[:80]
                    print(f"      [{role}]: {content_preview}...")
            
            # Generate response with error handling
            try:
                print(f"   🚀 Invoking {state.get('model')} LLM...")
                ai_response = llm.invoke(messages)
                response_preview = str(ai_response.content)[:100] if hasattr(ai_response, 'content') else str(ai_response)[:100]
                print(f"   ✅ LLM responded: {response_preview}...")
            except Exception as e:
                # LLM invocation failed - create error message
                error_msg = str(e).lower()
                
                # Import error handler here to avoid circular import
                from .llm import handle_llm_error, get_model_config
                
                # Get provider from model config
                try:
                    config = get_model_config(state.get("model", "command-r"))
                    provider = config.get("provider", "unknown")
                except:
                    provider = "unknown"
                
                # Get standardized error using the new handler
                error_info = handle_llm_error(e, provider)
                error_content = error_info['message']
                
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
        model: str,
        db_url: Optional[str] = None,
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
            db_url: Optional database URL for this request (overrides instance default)
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
            db_url=db_url,
            previous_response_id=previous_response_id,
            instructions=instructions,
            store=store,
            temperature=temperature,
            metadata=metadata
        )