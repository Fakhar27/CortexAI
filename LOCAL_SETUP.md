# 🏠 CortexAI Local Development Setup

This guide will help you get CortexAI running locally on your machine for development and testing.

## 📋 Prerequisites

- **Python 3.8+** (you have Python 3.13.7 ✅)
- **API Keys** for at least one LLM provider:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Google AI API Key](https://aistudio.google.com/app/apikey)
  - [Cohere API Key](https://dashboard.cohere.ai/api-keys)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./scripts/setup_local.sh
```

### Option 2: Manual Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -e .

# 3. Install web server dependencies (optional)
pip install fastapi uvicorn
```

## 🔑 Environment Variables

Set your API keys as environment variables:

```bash
# Required: At least one API key
export OPENAI_API_KEY="your-openai-key-here"
export GOOGLE_API_KEY="your-google-key-here"
export CO_API_KEY="your-cohere-key-here"

# Optional: Database URL for persistence
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### Adding to your shell profile (permanent setup)

Add these lines to your `~/.zshrc` or `~/.bashrc`:

```bash
# CortexAI API Keys
export OPENAI_API_KEY="your-openai-key-here"
export GOOGLE_API_KEY="your-google-key-here"
export CO_API_KEY="your-cohere-key-here"
```

## 🧪 Testing Your Setup

### 1. Basic Test

```bash
# Activate virtual environment
source venv/bin/activate

# Run basic test
python scripts/example_local.py
```

### 2. Conversation Test

```bash
# Test conversation persistence
python scripts/example_conversation.py
```

### 3. Web Server Test

```bash
# Start the web server
python scripts/example_web_server.py

# Visit http://localhost:8000/docs for API documentation
```

## 📚 Usage Examples

### Basic Usage

```python
from cortex import Client

# Initialize client (uses in-memory storage by default)
api = Client()

# Create a response
response = api.create(
    input="Hello! How are you?",
    model="gpt-4o-mini",
    instructions="You are a helpful assistant",
    store=True,
    temperature=0.7
)

print(response["message"]["content"])
```

### With Database Persistence

```python
from cortex import Client

# Initialize with SQLite for local development
api = Client(db_url="sqlite:///./conversations.db")

# Or with PostgreSQL for production
# api = Client(db_url="postgresql://user:pass@host:5432/db")

response = api.create(
    input="Tell me a joke",
    model="gemini-1.5-pro",
    store=True
)
```

### Continuing Conversations

```python
# First message
response1 = api.create(
    input="What's the weather like?",
    model="gpt-4o-mini",
    store=True
)

# Continue the conversation
response2 = api.create(
    input="What about tomorrow?",
    model="command-r",  # Can switch models mid-conversation
    previous_response_id=response1["id"],
    store=True
)
```

## 🌐 Web API Usage

Once you start the web server (`python example_web_server.py`), you can use the API:

### Using curl

```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Tell me a joke",
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

### Using Python requests

```python
import requests

response = requests.post("http://localhost:8000/chat", json={
    "message": "What is machine learning?",
    "model": "gemini-1.5-pro",
    "system_prompt": "You are a helpful AI tutor"
})

print(response.json())
```

## 🗄️ Database Options

### 1. In-Memory (Default)
- No persistence
- Good for testing
- Conversations lost on restart

```python
api = Client()  # Uses MemorySaver
```

### 2. SQLite (Local Development)
- File-based database
- Good for local development
- Conversations persist between runs

```python
api = Client(db_url="sqlite:///./conversations.db")
```

### 3. PostgreSQL (Production)
- Full database support
- Connection pooling compatible
- Production-ready

```python
api = Client(db_url="postgresql://user:pass@host:5432/db")
```

## 🤖 Supported Models

### OpenAI
- `gpt-4o` - Latest GPT-4 model
- `gpt-4o-mini` - Cost-effective option
- `gpt-4-turbo` - High-performance
- `gpt-3.5-turbo` - Fast and cheap

### Google Gemini
- `gemini-2.0-flash` - Latest flash model
- `gemini-2.5-flash` - Newest generation
- `gemini-1.5-pro` - Pro model for complex tasks

### Cohere
- `command-r-08-2024` - RAG-optimized
- `command-r-plus-08-2024` - Enhanced version

## 🔧 Troubleshooting

### Common Issues

1. **"No API key found" error**
   ```bash
   # Make sure your API keys are set
   echo $OPENAI_API_KEY
   echo $GOOGLE_API_KEY
   echo $CO_API_KEY
   ```

2. **Import errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall if needed
   pip install -e .
   ```

3. **Database connection errors**
   ```bash
   # For SQLite, make sure the directory is writable
   # For PostgreSQL, check connection string format
   ```

4. **Model not found errors**
   - Check the supported models list above
   - Ensure you have the correct API key for the provider
   - Some models may be deprecated - use the latest versions

### Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Look at the example files in this directory
- Check the API documentation at http://localhost:8000/docs when running the web server

## 🎯 Next Steps

1. **Explore the examples**: Try different models and conversation patterns
2. **Build your own app**: Use the API in your own Python applications
3. **Deploy to production**: Use Docker or serverless deployment options
4. **Contribute**: Check the main README for contribution guidelines

## 📁 Project Structure

```
CortexAI/
├── cortex/                 # Main package
│   ├── responses/         # API implementation
│   └── models/           # Model configurations
├── example_local.py      # Basic usage example
├── example_conversation.py # Conversation example
├── example_web_server.py # Web API example
├── setup_local.sh       # Setup script
└── LOCAL_SETUP.md       # This file
```

Happy coding! 🚀

