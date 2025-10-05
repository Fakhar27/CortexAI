#!/bin/bash

echo "🔑 CortexAI API Keys Setup"
echo "=========================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating now..."
    source venv/bin/activate
fi

echo "Please enter your API keys (press Enter to skip any you don't have):"
echo ""

# OpenAI API Key
read -p "OpenAI API Key: " openai_key
if [[ ! -z "$openai_key" ]]; then
    export OPENAI_API_KEY="$openai_key"
    echo "✅ OpenAI API key set"
else
    echo "⏭️  Skipped OpenAI API key"
fi

echo ""

# Google API Key
read -p "Google AI API Key: " google_key
if [[ ! -z "$google_key" ]]; then
    export GOOGLE_API_KEY="$google_key"
    echo "✅ Google AI API key set"
else
    echo "⏭️  Skipped Google AI API key"
fi

echo ""

# Cohere API Key
read -p "Cohere API Key: " cohere_key
if [[ ! -z "$cohere_key" ]]; then
    export CO_API_KEY="$cohere_key"
    echo "✅ Cohere API key set"
else
    echo "⏭️  Skipped Cohere API key"
fi

echo ""
echo "🔍 Verifying API keys..."

# Check which keys are set
keys_set=0
if [[ ! -z "$OPENAI_API_KEY" ]]; then
    echo "✅ OPENAI_API_KEY is set"
    keys_set=$((keys_set + 1))
fi

if [[ ! -z "$GOOGLE_API_KEY" ]]; then
    echo "✅ GOOGLE_API_KEY is set"
    keys_set=$((keys_set + 1))
fi

if [[ ! -z "$CO_API_KEY" ]]; then
    echo "✅ CO_API_KEY is set"
    keys_set=$((keys_set + 1))
fi

echo ""
if [[ $keys_set -eq 0 ]]; then
    echo "❌ No API keys were set. You need at least one to use CortexAI."
    echo "   Get API keys from:"
    echo "   - OpenAI: https://platform.openai.com/api-keys"
    echo "   - Google: https://aistudio.google.com/app/apikey"
    echo "   - Cohere: https://dashboard.cohere.ai/api-keys"
    exit 1
else
    echo "🎉 $keys_set API key(s) set successfully!"
    echo ""
    echo "🧪 Testing the setup..."
    python -c "
from cortex import Client
try:
    api = Client()
    print('✅ CortexAI client initialized successfully!')
    print('🚀 You can now run: python example_local.py')
except Exception as e:
    print(f'❌ Error: {e}')
"
fi

echo ""
echo "💡 To make these keys permanent, add them to your ~/.zshrc:"
echo "   echo 'export OPENAI_API_KEY=\"$OPENAI_API_KEY\"' >> ~/.zshrc"
echo "   echo 'export GOOGLE_API_KEY=\"$GOOGLE_API_KEY\"' >> ~/.zshrc"
echo "   echo 'export CO_API_KEY=\"$CO_API_KEY\"' >> ~/.zshrc"

