# Cortex - Open Source Alternative to OpenAI APIs

## Project Overview

Cortex is an ambitious open-source framework that provides OpenAI-compatible APIs using free LLMs and LangGraph. The project aims to democratize AI by creating a developer-friendly alternative to expensive proprietary AI services.

## Vision & Goals

### Primary Vision
Build a Python framework that replicates OpenAI's Assistants and Responses APIs, but with:
- **Free LLMs** - Using Cohere instead of expensive OpenAI models
- **Open Source** - Full transparency and community-driven development
- **Developer Friendly** - Simple APIs that hide LangGraph complexity
- **Local Control** - Data stays on your infrastructure

### Key Objectives
1. Create a pip-installable framework that developers can use like `from cortex import ResponsesAPI`
2. Provide OpenAI-compatible APIs that work with free LLMs
3. Enable multi-agent systems (like the 17-coach system) with simple configuration
4. Prove that expensive AI systems can be democratized by a single skilled engineer

## Current Development Status

### Completed Components

#### 1. Project Structure ✅
```
cortex/
├── cortex/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── registry.py      # LLM model configurations
│   └── responses/
│       ├── __init__.py
│       ├── api.py           # Main ResponsesAPI class (empty)
│       ├── state.py         # ResponsesState TypedDict
│       ├── llm.py           # LLM selection logic
│       └── methods/
│           ├── __init__.py
│           └── create.py    # Response creation method (partial)
├── data/                    # Documentation and planning files
├── example.py              # Usage example
├── pyproject.toml          # Package configuration
└── README.md              # Project documentation
```

#### 2. Core Implementations ✅

**State Management (cortex/responses/state.py)**
- `ResponsesState` TypedDict defining conversation state structure
- Uses LangGraph's `Annotated[List[BaseMessage], add_messages]` for message accumulation
- Includes fields for conversation tracking, instructions, and model selection

**LLM Integration (cortex/responses/llm.py)**
- `get_llm()` function with provider-based switching
- Currently supports Cohere with command-r model
- Extensible design for adding OpenAI, Anthropic, etc.

**Model Registry (cortex/models/registry.py)**
- Centralized model configurations
- Easy to add new models and providers
- Temperature and other settings management

### In Progress Components 🚧

**ResponsesAPI Implementation (cortex/responses/api.py)**
- Main API class structure planned
- Need to implement LangGraph StateGraph setup
- Conversation persistence with checkpointing
- OpenAI-compatible response formatting

**Create Method (cortex/responses/methods/create.py)**
- Basic structure in place
- ID generation logic implemented
- TODO: Graph invocation and response formatting

### Planned Features 📋

1. **Complete Responses API**
   - Finish create() method implementation
   - Add retrieve() and delete() methods
   - Implement conversation persistence

2. **Multi-Agent Support**
   - Router for directing to different agents
   - 17-coach system as demonstration
   - Dynamic agent creation

3. **Assistants API**
   - More complex than Responses API
   - Thread management
   - Tool integration

4. **HTTP API Layer**
   - FastAPI wrapper for REST endpoints
   - Next.js integration support
   - WebSocket support for streaming

## Technical Architecture

### Core Technologies
- **LangGraph** - For conversation state management and flow control
- **LangChain** - For LLM integrations and message handling
- **Cohere** - Free LLM provider for MVP
- **SQLite** - Local conversation persistence

### Key Design Patterns

1. **State Management**
   - TypedDict for type-safe state definition
   - Annotated types for automatic message accumulation
   - Checkpointing for conversation persistence

2. **Provider Abstraction**
   - Factory pattern for LLM selection
   - Registry pattern for model configurations
   - Easy provider switching

3. **API Compatibility**
   - Match OpenAI's request/response format
   - Support previous_response_id for conversation continuity
   - Instructions for dynamic behavior

## Development Philosophy

### Simplicity First
- Hide LangGraph complexity behind simple APIs
- Make it as easy as `api.create(input="Hello")`
- Clear, focused modules

### Open Source Values
- Full transparency in implementation
- Community-driven development
- Free alternatives to expensive services

### Developer Experience
- Pip-installable package
- Clear documentation with examples
- Type hints and IDE support

## Next Steps

1. **Complete ResponsesAPI Implementation**
   - Implement StateGraph in api.py
   - Finish create() method with graph invocation
   - Add conversation persistence

2. **Testing & Examples**
   - Create comprehensive test suite
   - Build coaching app demonstration
   - Document API usage patterns

3. **Community Building**
   - Publish to PyPI
   - Create GitHub repository
   - Write blog posts and tutorials

## Long-term Vision

### Framework Ecosystem
- Multiple API implementations (Responses, Assistants, etc.)
- Plugin system for custom agents
- Integration templates for popular frameworks

### Business Impact
- Enable startups who can't afford OpenAI
- Provide enterprises with data control
- Foster innovation in AI applications

### Technical Evolution
- Support for more LLM providers
- Advanced routing and orchestration
- Performance optimizations

## Conclusion

Cortex represents a significant step toward democratizing AI technology. By providing OpenAI-compatible APIs with free LLMs, it enables developers and businesses to build sophisticated AI applications without the high costs and vendor lock-in of proprietary services.

The project is currently in early development, with the core architecture in place and the Responses API partially implemented. The next phase focuses on completing the implementation and demonstrating its capabilities through a multi-agent coaching system.

This framework has the potential to make advanced AI capabilities accessible to everyone, proving that what was once a $400K enterprise solution can be built by a single determined engineer using open-source tools.