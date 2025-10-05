# 🛠️ CortexAI Scripts

This folder contains utility scripts and examples to help you get started with CortexAI locally.

## 📁 Script Overview

| Script | Type | Description |
|--------|------|-------------|
| `setup_local.sh` | Setup | Automated local environment setup |
| `setup_api_keys.sh` | Setup | Interactive API key configuration |
| `validate_database.py` | Utility | Database connection validation |
| `edit_env.py` | Utility | .env file editor helper |
| `example_local.py` | Example | Basic usage demonstration |
| `example_conversation.py` | Example | Multi-model conversation example |
| `example_web_server.py` | Example | FastAPI web server |
| `env_template.txt` | Template | .env file template |

## 🚀 Quick Start

### 1. Automated Setup (Recommended)
```bash
# Run the complete setup
./scripts/setup_local.sh
```

### 2. Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Set up API keys
./scripts/setup_api_keys.sh
```

## 📋 Script Details

### Setup Scripts

#### `setup_local.sh`
**Purpose**: Complete automated setup for local development
```bash
./scripts/setup_local.sh
```
**What it does**:
- Creates virtual environment
- Installs all dependencies
- Installs FastAPI/Uvicorn for web server
- Provides next steps instructions

#### `setup_api_keys.sh`
**Purpose**: Interactive API key configuration
```bash
./scripts/setup_api_keys.sh
```
**What it does**:
- Prompts for OpenAI, Google, and Cohere API keys
- Sets environment variables
- Validates the setup
- Shows how to make keys permanent

### Utility Scripts

#### `validate_database.py`
**Purpose**: Test and validate database connections
```bash
# Validate current DATABASE_URL from .env
python scripts/validate_database.py

# Validate specific URL
python scripts/validate_database.py "postgresql://user:pass@host:5432/db"
```
**What it does**:
- Tests PostgreSQL and SQLite connections
- Validates PostgresSaver setup
- Tests CortexAI integration
- Provides troubleshooting tips

#### `edit_env.py`
**Purpose**: Helper for editing .env file
```bash
python scripts/edit_env.py
```
**What it does**:
- Shows current .env contents
- Provides editing instructions
- Lists API key sources

### Example Scripts

#### `example_local.py`
**Purpose**: Basic CortexAI usage demonstration
```bash
python scripts/example_local.py
```
**What it does**:
- Initializes CortexAI client
- Creates a simple response
- Shows response format
- Handles errors gracefully

#### `example_conversation.py`
**Purpose**: Multi-model conversation with persistence
```bash
python scripts/example_conversation.py
```
**What it does**:
- Demonstrates conversation continuity
- Shows model switching mid-conversation
- Uses SQLite for local persistence
- Creates a multi-turn dialogue

#### `example_web_server.py`
**Purpose**: FastAPI web server with REST API
```bash
python scripts/example_web_server.py
```
**What it does**:
- Starts FastAPI server on port 8000
- Provides REST API endpoints
- Auto-generates API documentation
- Handles chat requests

## 🔧 Configuration Files

### `env_template.txt`
Template for creating your `.env` file:
```bash
# Copy template to .env
cp scripts/env_template.txt .env

# Edit with your API keys
nano .env
```

## 🎯 Usage Examples

### Basic Testing
```bash
# 1. Set up environment
./scripts/setup_local.sh

# 2. Configure API keys
./scripts/setup_api_keys.sh

# 3. Test basic functionality
python scripts/example_local.py
```

### Database Setup
```bash
# 1. Add DATABASE_URL to .env
echo "DATABASE_URL=postgresql://user:pass@localhost:5432/cortex" >> .env

# 2. Validate database connection
python scripts/validate_database.py

# 3. Test with persistence
python scripts/example_conversation.py
```

### Web Server
```bash
# 1. Start the web server
python scripts/example_web_server.py

# 2. Visit API documentation
open http://localhost:8000/docs

# 3. Test with curl
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "gpt-4o-mini"}'
```

## 🔑 API Keys Setup

### Required Keys
You need at least one API key from these providers:

- **OpenAI**: https://platform.openai.com/api-keys
- **Google AI**: https://aistudio.google.com/app/apikey
- **Cohere**: https://dashboard.cohere.ai/api-keys

### Setting Keys
```bash
# Option 1: Interactive setup
./scripts/setup_api_keys.sh

# Option 2: Manual .env editing
python scripts/edit_env.py
# Then edit .env file with your keys

# Option 3: Environment variables
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
export CO_API_KEY="your-key"
```

## 🗄️ Database Options

### SQLite (Default)
```bash
# No DATABASE_URL needed - uses SQLite automatically
python scripts/example_conversation.py
```

### PostgreSQL
```bash
# Add to .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/cortex

# Validate connection
python scripts/validate_database.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"No API key found"**
   ```bash
   # Check if keys are set
   python scripts/edit_env.py
   ```

2. **Database connection errors**
   ```bash
   # Validate your database
   python scripts/validate_database.py
   ```

3. **Import errors**
   ```bash
   # Reinstall dependencies
   ./scripts/setup_local.sh
   ```

4. **Permission errors**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   ```

### Getting Help

- Check the main [README.md](../README.md) for detailed documentation
- Look at the example scripts for usage patterns
- Run validation scripts to diagnose issues
- Check the API documentation at http://localhost:8000/docs when running the web server

## 📚 Next Steps

1. **Explore Examples**: Try different models and conversation patterns
2. **Build Your App**: Use the API in your own Python applications
3. **Deploy**: Use Docker or serverless deployment options
4. **Contribute**: Check the main README for contribution guidelines

## 🔗 Related Files

- [Main README](../README.md) - Complete project documentation
- [Local Setup Guide](../LOCAL_SETUP.md) - Detailed local development guide
- [Quick Start](../QUICK_START.md) - Quick reference guide
- [.env file](../.env) - Your API keys and configuration

---

**Happy coding with CortexAI!** 🚀
