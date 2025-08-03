# Cortex Development Error Analysis Report

## Executive Summary
During the development of Cortex, we encountered several critical errors that delayed our progress. This report analyzes each error, explains what went wrong, and provides solutions to avoid similar issues in future development.

## Error Timeline and Analysis

### 1. Import Error: `add_messages` from wrong module
**Error:**
```python
ImportError: cannot import name 'add_messages' from 'langchain_core.messages'
```

**Root Cause:**
- We imported `add_messages` from `langchain_core.messages` based on outdated documentation
- The function was actually moved to `langgraph.graph` in newer versions

**Solution Applied:**
```python
# Wrong
from langchain_core.messages import add_messages

# Correct
from langgraph.graph import add_messages
```

**Lesson Learned:**
- Always verify imports with the latest documentation
- Use IDE autocomplete to confirm module locations
- Keep a reference of working imports from existing projects

### 2. SQLite Checkpointer Connection Error
**Error:**
```python
sqlite3.ProgrammingError: Cannot operate on a closed database
AttributeError: '_GeneratorContextManager' object has no attribute 'get_next_version'
```

**Root Cause:**
- `SqliteSaver.from_conn_string()` returns a context manager, not a direct checkpointer instance
- We were trying to use it as a regular object, causing the connection to close immediately
- Documentation examples showed both patterns, causing confusion

**Initial Wrong Approach:**
```python
# This returns a context manager that closes immediately
checkpointer = SqliteSaver.from_conn_string("conversations.db")
```

**Solution Applied:**
```python
# Create connection directly and pass to SqliteSaver
conn = sqlite3.connect(path, check_same_thread=False)
checkpointer = SqliteSaver(conn)
```

**Lesson Learned:**
- Read documentation examples carefully - distinguish between context manager and direct usage
- When dealing with database connections, understand the lifecycle management
- Test persistence early in development, not as an afterthought

### 3. Cohere Version Compatibility Issues
**Error:**
```python
ImportError: cannot import name 'ChatResponse' from 'cohere.types'
```

**Root Cause:**
- Version mismatch between `cohere` and `langchain-cohere` packages
- Latest versions had breaking changes in type definitions
- pip installed latest versions by default, which were incompatible

**Solution Applied:**
```txt
# requirements.txt - Pin specific working versions
cohere==5.13.11
langchain-cohere==0.4.2
```

**Lesson Learned:**
- Always pin package versions in requirements.txt
- Test with specific versions before assuming latest will work
- Keep a working requirements.txt from previous projects as reference

### 4. Environment Variable Not Loading
**Error:**
```python
cohere.core.api_error.ApiError: The client must be instantiated be either passing in token or setting CO_API_KEY
```

**Root Cause:**
- `.env` file existed but wasn't being loaded automatically
- Python doesn't load `.env` files by default
- Environment variable was set in shell but not available to Python process

**Solution Applied:**
```python
# Added to llm.py
from dotenv import load_dotenv
load_dotenv()  # This loads .env file
```

**Lesson Learned:**
- Always use `python-dotenv` for environment variables
- Load `.env` at the module level, not just in main
- Document all required environment variables

## Best Practices for Future Development

### 1. Project Setup Checklist
```bash
# Always start with:
1. Create virtual environment
2. Create requirements.txt with pinned versions
3. Create .env file with all API keys
4. Test basic imports before building features
```

### 2. Import Management
```python
# Keep a working imports reference file
# cortex/imports_reference.py
"""
Working imports for Cortex project:
- from langgraph.graph import StateGraph, END, add_messages
- from langgraph.checkpoint.sqlite import SqliteSaver
- from langchain_cohere import ChatCohere
- import sqlite3 for direct connection
"""
```

### 3. Error Debugging Strategy
1. **Read the full error traceback** - The actual error is often at the bottom
2. **Check package versions** - Most import errors are version mismatches
3. **Verify with minimal examples** - Test components in isolation
4. **Keep documentation links** - Save working examples from docs

### 4. Database Connection Pattern
```python
# Always use this pattern for SQLite in LangGraph:
def get_sqlite_checkpointer(db_path: str):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    return SqliteSaver(conn)
```

### 5. Package Version Management
```python
# Create a test script to verify all imports
# test_imports.py
try:
    from langgraph.graph import StateGraph, add_messages
    print("✓ LangGraph imports OK")
except ImportError as e:
    print(f"✗ LangGraph import failed: {e}")
```

## Optimization Recommendations

### 1. Development Workflow
- Start with a working template/boilerplate
- Test each component before integration
- Keep error logs with solutions for future reference

### 2. Dependency Management
- Use `pip freeze > requirements.txt` after confirming everything works
- Document why specific versions are needed
- Consider using `poetry` or `pipenv` for better dependency management

### 3. Testing Strategy
- Create simple test files for each major component
- Test persistence immediately, not as final step
- Use mock LLMs for testing to avoid API costs

### 4. Documentation
- Document working code snippets
- Keep notes on what doesn't work and why
- Link to specific documentation versions used

## Conclusion

The main issues we faced were:
1. Using outdated import paths
2. Misunderstanding database connection patterns
3. Package version incompatibilities
4. Environment configuration issues

By following the practices outlined in this report, future development should be more efficient and encounter fewer blocking errors. The key is to verify basic functionality early and maintain good documentation of what works.

## Quick Reference for Common Issues

| Error Type | Quick Fix |
|------------|-----------|
| Import not found | Check package version and documentation |
| SQLite connection closed | Use direct connection, not context manager |
| API key not found | Use `load_dotenv()` at module level |
| Version conflict | Pin all versions in requirements.txt |