"""Check available LangGraph modules"""
import langgraph
import langgraph.checkpoint

print("LangGraph version:", langgraph.__version__)
print("\nAvailable in langgraph.checkpoint:")
print(dir(langgraph.checkpoint))

try:
    from langgraph.checkpoint.memory import MemorySaver
    print("\n✓ MemorySaver available")
except:
    print("\n✗ MemorySaver not available")

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    print("✓ SqliteSaver available at langgraph.checkpoint.sqlite")
except:
    try:
        from langgraph.checkpoint import SqliteSaver
        print("✓ SqliteSaver available at langgraph.checkpoint")
    except:
        print("✗ SqliteSaver not available")