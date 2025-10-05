#!/bin/bash

echo "🚀 CortexAI Local Setup Script"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -e .

# Install FastAPI and Uvicorn for web server example
echo "🌐 Installing web server dependencies..."
pip install fastapi uvicorn

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔑 Next steps:"
echo "1. Set your API keys as environment variables:"
echo "   export OPENAI_API_KEY='your-openai-key'"
echo "   export GOOGLE_API_KEY='your-google-key'"
echo "   export CO_API_KEY='your-cohere-key'"
echo ""
echo "2. Test the basic setup:"
echo "   python example_local.py"
echo ""
echo "3. Test conversation persistence:"
echo "   python example_conversation.py"
echo ""
echo "4. Start the web server:"
echo "   python example_web_server.py"
echo ""
echo "5. Access the API docs at: http://localhost:8000/docs"
echo ""
echo "📚 For more examples, check the README.md file"

