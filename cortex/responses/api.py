"""Main ResponsesAPI class - orchestrates the Responses API functionality"""
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .state import ResponsesState
from .persistence import get_checkpointer
from .llm import get_llm
from .methods.create import create_response
from .methods.retrieve import retrieve_response


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
            
            if db_path is not None:
                import warnings
                warnings.warn(
                    "db_path parameter is deprecated. "
                    "Use db_url for PostgreSQL or leave empty for local SQLite.",
                    DeprecationWarning,
                    stacklevel=2
                )
                if db_url is None:
                    parent_dir = os.path.dirname(db_path)
                    if parent_dir and not os.path.exists(parent_dir):
                        raise ValueError(f"Database directory does not exist: {parent_dir}")
            
            try:
                self.checkpointer = get_checkpointer(db_url=db_url)
                self.db_url = db_url
            except DatabaseError as e:
                raise e
            except Exception as e:
                raise RuntimeError(f"Failed to initialize database: {str(e)}")
            
            try:
                self.graph = self._setup_graph()
            except Exception as e:
                raise RuntimeError(f"Failed to setup graph workflow: {str(e)}")
                
        except DatabaseError:
            raise
        except Exception as e:
            raise RuntimeError(f"ResponsesAPI initialization failed: {str(e)}")
    
    def _setup_graph(self) -> StateGraph:
        """
        Set up the LangGraph workflow
        
        Returns:
            Compiled StateGraph with checkpointer
        """
        workflow = StateGraph(ResponsesState)
        
        workflow.add_node("generate", self._generate_node)
        
        workflow.set_entry_point("generate")
        
        workflow.add_edge("generate", END)
        
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
            
            temperature = state.get("temperature")
            llm = get_llm(state["model"], temperature=temperature)
            
            messages = list(state["messages"])  
            
            has_system_msg = any(isinstance(msg, SystemMessage) for msg in messages)
            if has_system_msg:
                print(f"   Instructions: Yes (from checkpoint)")
            elif state.get("instructions"):
                print(f"   Instructions: Yes (but not in messages - this is a bug!)")
            print(f"   Total messages to LLM: {len(messages)}")
            
            if len(messages) > 1:
                print(f"   📜 Conversation history:")
                for i, msg in enumerate(messages[-3:]):  
                    role = msg.__class__.__name__.replace("Message", "")
                    content_preview = str(msg.content)[:80] if hasattr(msg, 'content') else str(msg)[:80]
                    print(f"      [{role}]: {content_preview}...")
            
            try:
                print(f"   🚀 Invoking {state.get('model')} LLM...")
                ai_response = llm.invoke(messages)
                response_preview = str(ai_response.content)[:100] if hasattr(ai_response, 'content') else str(ai_response)[:100]
                print(f"   ✅ LLM responded: {response_preview}...")
            except Exception as e:
                error_msg = str(e).lower()
                
                from .llm import handle_llm_error, get_model_config
                
                try:
                    config = get_model_config(state.get("model", "command-r"))
                    provider = config.get("provider", "unknown")
                except:
                    provider = "unknown"
                
                error_info = handle_llm_error(e, provider)
                error_content = error_info['message']
                
                ai_response = AIMessage(content=f"Error: {error_content}")
            
            return {
                "messages": [ai_response]  
            }
            
        except Exception as e:
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

    def retrieve(
        self,
        response_id: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve a conversation's messages by response_id or thread_id.

        Args:
            response_id: A specific response ID within a conversation.
            thread_id: Stable conversation/thread ID.

        Returns:
            Dict with keys: conversation_id, messages (list of {role, content}).
        """
        return retrieve_response(self, response_id=response_id, thread_id=thread_id)
