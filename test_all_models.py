#!/usr/bin/env python3
"""
Local Model Testing Script
Tests all models to identify which providers are working vs failing
"""
import os
import sys
from typing import Dict, Any

def test_provider_imports():
    """Test importing each provider and show detailed error info"""
    print("=" * 60)
    print("PROVIDER IMPORT TESTING")
    print("=" * 60)
    
    # Test Cohere
    print("\n1. COHERE PROVIDER:")
    print("-" * 20)
    try:
        from langchain_cohere import ChatCohere
        print("✅ langchain_cohere.ChatCohere imported successfully")
        
        # Test deeper import that's causing the issue
        try:
            from cohere.types import ChatResponse
            print("✅ cohere.types.ChatResponse imported successfully")
        except ImportError as e:
            print(f"❌ cohere.types.ChatResponse import failed: {e}")
            
        # Check cohere package version
        try:
            import cohere
            print(f"📦 cohere package version: {cohere.__version__}")
        except:
            print("❌ Cannot determine cohere package version")
            
        # Check what's actually in cohere.types
        try:
            import cohere.types
            available_types = dir(cohere.types)
            print(f"📋 Available in cohere.types: {[t for t in available_types if not t.startswith('_')]}")
        except Exception as e:
            print(f"❌ Cannot inspect cohere.types: {e}")
            
    except ImportError as e:
        print(f"❌ langchain_cohere import failed: {e}")
    
    # Test OpenAI
    print("\n2. OPENAI PROVIDER:")
    print("-" * 20)
    try:
        from langchain_openai import ChatOpenAI
        print("✅ langchain_openai.ChatOpenAI imported successfully")
    except ImportError as e:
        print(f"❌ langchain_openai import failed: {e}")
    
    # Test Google
    print("\n3. GOOGLE PROVIDER:")
    print("-" * 20)
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai.ChatGoogleGenerativeAI imported successfully")
    except ImportError as e:
        print(f"❌ langchain_google_genai import failed: {e}")
    
    # Test Anthropic
    print("\n4. ANTHROPIC PROVIDER:")
    print("-" * 20)
    try:
        from langchain_anthropic import ChatAnthropic
        print("✅ langchain_anthropic.ChatAnthropic imported successfully")
    except ImportError as e:
        print(f"❌ langchain_anthropic import failed: {e}")

def test_cortex_model_registry():
    """Test our model registry and LLM initialization"""
    print("\n" + "=" * 60)
    print("CORTEX MODEL REGISTRY TESTING")
    print("=" * 60)
    
    try:
        from cortex.models.registry import MODELS
        from cortex.responses.llm import get_llm
        
        print(f"\n📋 Total models in registry: {len(MODELS)}")
        
        # Group by provider
        by_provider = {}
        for model_id, config in MODELS.items():
            provider = config['provider']
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(model_id)
        
        for provider, models in by_provider.items():
            print(f"  {provider}: {models}")
        
        # Test each model initialization
        print(f"\n🧪 Testing model initialization:")
        print("-" * 40)
        
        for model_id in MODELS.keys():
            print(f"\nTesting {model_id}...")
            try:
                llm = get_llm(model_id, temperature=0.7)
                print(f"  ✅ {model_id} initialized successfully")
                print(f"     Type: {type(llm).__name__}")
            except Exception as e:
                print(f"  ❌ {model_id} failed: {str(e)[:100]}...")
                
    except Exception as e:
        print(f"❌ Failed to test model registry: {e}")

def test_actual_llm_calls():
    """Test actual LLM calls with a simple prompt"""
    print("\n" + "=" * 60)
    print("ACTUAL LLM CALL TESTING")
    print("=" * 60)
    
    test_message = "Hello, respond with just 'Hi from [model name]'"
    
    try:
        from cortex.responses.llm import get_llm
        from cortex.models.registry import MODELS
        
        # Test a few key models if API keys are available
        test_models = ["gpt-4o-mini", "command-r", "gemini-1.5-flash"]
        
        for model_id in test_models:
            if model_id not in MODELS:
                continue
                
            config = MODELS[model_id]
            api_key_env = config.get("api_key_env")
            
            print(f"\n🧪 Testing {model_id}:")
            print(f"   API Key Env: {api_key_env}")
            
            if api_key_env and not os.getenv(api_key_env):
                print(f"   ⏭️  Skipped - no {api_key_env} environment variable")
                continue
            
            try:
                llm = get_llm(model_id, temperature=0.1)
                response = llm.invoke([{"role": "user", "content": test_message}])
                print(f"   ✅ Response: {response.content[:100]}...")
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:100]}...")
                
    except Exception as e:
        print(f"❌ Failed to test LLM calls: {e}")

def test_package_versions():
    """Show installed package versions"""
    print("\n" + "=" * 60)
    print("INSTALLED PACKAGE VERSIONS")
    print("=" * 60)
    
    packages = [
        "langchain-cohere",
        "langchain-openai", 
        "langchain-google-genai",
        "langchain-anthropic",
        "cohere",
        "openai",
        "google-generativeai",
        "anthropic",
        "langgraph",
        "langchain-core"
    ]
    
    for package in packages:
        try:
            import importlib.metadata
            version = importlib.metadata.version(package)
            print(f"  {package:25} {version}")
        except importlib.metadata.PackageNotFoundError:
            print(f"  {package:25} NOT INSTALLED")
        except Exception as e:
            print(f"  {package:25} ERROR: {e}")

def main():
    """Run all tests"""
    print("🧪 COMPREHENSIVE MODEL TESTING SCRIPT")
    print("Testing all providers and models to identify issues")
    
    test_package_versions()
    test_provider_imports()
    test_cortex_model_registry()
    
    print("\n" + "=" * 60)
    print("API KEY CHECK")
    print("=" * 60)
    api_keys = [
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY", 
        "CO_API_KEY",
        "ANTHROPIC_API_KEY"
    ]
    
    for key in api_keys:
        value = os.getenv(key)
        if value:
            print(f"  {key:20} ✅ Present ({value[:10]}...)")
        else:
            print(f"  {key:20} ❌ Missing")
    
    test_actual_llm_calls()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()