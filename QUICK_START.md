# 🚀 CortexAI Quick Start Guide

## ✅ Setup Complete!

Your CortexAI project is now ready to run locally! Here's what we've set up:

### 📦 What's Installed
- ✅ Python virtual environment (`venv/`)
- ✅ All CortexAI dependencies
- ✅ FastAPI and Uvicorn for web server
- ✅ Example scripts and documentation

### 🔑 Next Steps

1. **Set your API keys** (at least one required):
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export GOOGLE_API_KEY="your-google-key"  
   export CO_API_KEY="your-cohere-key"
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Test the setup**:
   ```bash
   python scripts/example_local.py
   ```

## 🎯 Available Examples

| File | Description | Command |
|------|-------------|---------|
| `scripts/example_local.py` | Basic usage test | `python scripts/example_local.py` |
| `scripts/example_conversation.py` | Multi-model conversation | `python scripts/example_conversation.py` |
| `scripts/example_web_server.py` | Web API server | `python scripts/example_web_server.py` |

## 🌐 Web Server

Start the web server to get a REST API:
```bash
python scripts/example_web_server.py
```

Then visit:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 Documentation

- **Full Setup Guide**: [LOCAL_SETUP.md](LOCAL_SETUP.md)
- **Main Documentation**: [README.md](README.md)

## 🆘 Need Help?

1. Check the [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed instructions
2. Look at the example files for usage patterns
3. Make sure your API keys are set correctly
4. Verify your internet connection

## 🎉 You're Ready!

Your CortexAI project is now set up and ready for local development. Happy coding! 🚀

