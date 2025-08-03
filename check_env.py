"""Check environment and dependencies"""
import sys
import subprocess

print("Python path:", sys.executable)
print("Python version:", sys.version)
print("\nInstalled packages:")

try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    if "langchain" in result.stdout:
        print("\nLangChain packages found:")
        for line in result.stdout.split('\n'):
            if 'langchain' in line or 'langgraph' in line:
                print(f"  {line}")
    else:
        print("\n❌ No LangChain packages found!")
        print("\nPlease run:")
        print("  pip install -r requirements.txt")
except Exception as e:
    print(f"Error checking packages: {e}")