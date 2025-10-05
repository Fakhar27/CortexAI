#!/usr/bin/env python3
"""
Simple script to help edit the .env file with your API keys
"""

import os
import sys

def main():
    env_file = ".env"
    
    print("🔑 CortexAI .env File Editor")
    print("=" * 30)
    print()
    
    # Check if .env file exists
    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found!")
        print("Creating a new one...")
        
        # Create basic .env file
        with open(env_file, 'w') as f:
            f.write("""# CortexAI API Keys
# This file is automatically loaded by python-dotenv

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your-openai-key-here

# Google AI API Key (get from https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY=your-google-key-here

# Cohere API Key (get from https://dashboard.cohere.ai/api-keys)
CO_API_KEY=your-cohere-key-here

# Optional: Database URL for persistence
# DATABASE_URL=postgresql://user:pass@host:5432/db
""")
        print(f"✅ Created {env_file}")
    
    print(f"📝 Current {env_file} contents:")
    print("-" * 40)
    
    with open(env_file, 'r') as f:
        content = f.read()
        print(content)
    
    print("-" * 40)
    print()
    print("✏️  To edit your API keys:")
    print(f"   1. Open {env_file} in your editor")
    print("   2. Replace 'your-*-key-here' with your actual API keys")
    print("   3. Save the file")
    print()
    print("🔗 Get API keys from:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - Google: https://aistudio.google.com/app/apikey")
    print("   - Cohere: https://dashboard.cohere.ai/api-keys")
    print()
    print("🧪 After editing, test with:")
    print("   python example_local.py")

if __name__ == "__main__":
    main()

