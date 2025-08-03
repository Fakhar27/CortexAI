"""Check what's available in langgraph.checkpoint"""
import langgraph.checkpoint

print("LangGraph checkpoint modules:")
print(dir(langgraph.checkpoint))

print("\nTrying to import different checkpointers:")

# Try MemorySaver
try:
    from langgraph.checkpoint.memory import MemorySaver
    print("✓ MemorySaver imported successfully")
except ImportError as e:
    print(f"✗ MemorySaver import failed: {e}")

# Try SqliteSaver from different locations
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    print("✓ SqliteSaver imported from langgraph.checkpoint.sqlite")
except ImportError:
    try:
        from langgraph.checkpoint import SqliteSaver
        print("✓ SqliteSaver imported from langgraph.checkpoint")
    except ImportError:
        print("✗ SqliteSaver not found in standard locations")

# Check if we need a separate package
print("\nNote: SqliteSaver might require 'langgraph-checkpoint-sqlite' package")
print("Try: pip install langgraph-checkpoint-sqlite")