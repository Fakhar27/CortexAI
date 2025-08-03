"""Check package versions"""
import subprocess
import sys

packages = ['cohere', 'langchain-cohere', 'langchain-core', 'langgraph']

print("Installed versions:")
for package in packages:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Name:') or line.startswith('Version:'):
                print(f"  {line}")
        print()
    except:
        print(f"  {package}: Not installed\n")