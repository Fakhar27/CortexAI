#!/usr/bin/env python3
"""
Test runner for Cortex
Run this to execute all tests and see what needs fixing
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return result.returncode == 0


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                  CORTEX TEST SUITE                       ║
║          Testing Your OpenAI Alternative                 ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov"])
    
    # Check for API key
    if not os.environ.get("CO_API_KEY"):
        print("""
⚠️  WARNING: CO_API_KEY not set!
Some tests will fail without Cohere API key.
Set it with: export CO_API_KEY='your-key-here'
        """)
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    tests = [
        ("Critical Tests Only", "pytest tests/test_core_functionality.py -v -m critical"),
        ("All Core Functionality", "pytest tests/test_core_functionality.py -v"),
        ("OpenAI Compatibility", "pytest tests/test_openai_compatibility.py -v"),
        ("Edge Cases", "pytest tests/test_edge_cases.py -v"),
        ("Full Test Suite", "pytest tests/ -v"),
        ("Coverage Report", "pytest tests/ --cov=cortex --cov-report=term-missing"),
    ]
    
    print("\nSelect tests to run:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"{i}. {name}")
    print("0. Exit")
    
    choice = input("\nEnter choice (1-6): ")
    
    if choice == "0":
        sys.exit(0)
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tests):
            name, cmd = tests[idx]
            success = run_command(cmd, name)
            
            if success:
                print("\n✅ Tests passed!")
            else:
                print("\n❌ Some tests failed. Review output above.")
                
                # Offer to run specific failing test
                print("\nTip: Run failing test individually for details:")
                print("  pytest tests/test_file.py::TestClass::test_method -vv")
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")
    
    # Summary
    print(f"\n{'='*60}")
    print("TESTING RECOMMENDATIONS:")
    print('='*60)
    print("""
1. Fix CRITICAL tests first (basic functionality)
2. Then fix OpenAI compatibility issues  
3. Finally handle edge cases

Run with coverage to see untested code:
  pytest tests/ --cov=cortex --cov-report=html
  open htmlcov/index.html
    """)


if __name__ == "__main__":
    main()