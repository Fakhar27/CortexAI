# Cortex - OpenAI Responses API Alternative

**🚀 Production Ready**: Cortex has evolved from beta with critical stability improvements and is now production-ready for serverless deployments.

**📅 Latest Updates (October 2025):**
- ✅ Fixed PostgreSQL pooler compatibility issues (Supabase, pgBouncer)
- ✅ Resolved GSSAPI authentication errors in Lambda
- ✅ Added automatic transaction recovery for fresh databases
- ✅ Updated to latest Gemini models (2.0-flash, 2.5-flash)
- ✅ Enhanced pipeline error handling with graceful recovery
- ✅ Production Docker images available on [Docker Hub](https://hub.docker.com/repository/docker/reaper27/cortex-api/general)

Cortex is a powerful Python framework that replicates OpenAI's Responses API functionality with multi-provider LLM support, advanced conversation persistence, and both local and serverless deployment capabilities.

## Why Cortex?

### Advantages Over OpenAI Responses API
- **Multi-Provider Support**: Use OpenAI, Google Gemini, Cohere, and Opensource local models seamlessly
- **Cost Effective**: Access to free and cheaper LLM alternatives 
- **Cross-Model Conversations**: Switch models mid-conversation while maintaining context
- **Flexible Deployment**: Local development, Docker containers, and serverless (AWS Lambda)
- **Advanced Persistence**: Sophisticated checkpointing system with PostgreSQL and SQLite support
- **Pooler Compatible**: Works with connection poolers like Supabase with proper threading locks
- **Open Source**: Full control and transparency

### Current Limitations
- **No Streaming**: Responses are returned as complete messages only
- **No Tool Calling**: Function/tool calling not yet implemented
- **Beta Stability**: Production-ready but actively evolving
  - Connection pooler issues are automatically handled with retry logic
  - Pipeline mode errors include graceful recovery
  - All critical issues from initial beta have been resolved

## Architecture

Cortex uses a sophisticated checkpointing system for conversation persistence:

- **persistence.py**: Advanced connection pooler detection with automatic fallback handling
  - Automatic detection of Supabase and other pooled connections
  - GSSAPI authentication disabled for Lambda compatibility
  - Autocommit mode for DDL operations with pooled connections
  - Graceful pipeline error recovery with user-friendly messages
- **create.py**: Handles initial conversation state and instructions persistence following OpenAI spec  
  - Enhanced pipeline error detection and retry logic
  - Transaction rollback handling for failed operations
- **api.py**: Core orchestration with error handling and LLM invocation
- **models/registry.py**: Multi-provider model configurations with latest model updates

The system automatically detects connection poolers (like Supabase) and applies appropriate connection handling to prevent pipeline mode conflicts and transaction blocking issues.

## Supported Models

### OpenAI
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`

### Google Gemini (Updated October 2025)
- `gemini-2.0-flash` - Latest flash model with improved performance
- `gemini-2.5-flash` - Newest generation flash model  
- `gemini-1.5-pro` - Pro model for complex tasks

### Cohere (Updated October 2025)
- `command-r-08-2024` - Efficient RAG-optimized model
- `command-r-plus-08-2024` - Enhanced version with better performance


## Database Support

- **PostgreSQL**: Full production support with connection pooler compatibility
- **SQLite**: Local development and testing
- **MemorySaver**: In-memory conversations (non-persistent)

## Installation & Deployment

### 🐳 Docker Hub (Recommended - Instant Deployment!)

**✨ Pre-built production images available on Docker Hub - No build required!**

🔗 **Docker Hub Repository**: [**reaper27/cortex-api**](https://hub.docker.com/repository/docker/reaper27/cortex-api/general)

```bash
# Pull the latest production-ready image (317MB compressed)
docker pull reaper27/cortex-api:latest

# Run locally with your API keys
docker run -p 8080:8080 \
  -e CO_API_KEY="your-cohere-key" \
  -e OPENAI_API_KEY="your-openai-key" \
  -e GOOGLE_API_KEY="your-google-key" \
  -e DATABASE_URL="postgresql://..." \
  reaper27/cortex-api:latest
```

**Why Docker Hub?**
- ✅ Pre-built and tested images
- ✅ Instant deployment without building
- ✅ Optimized for production use
- ✅ Regular updates with latest fixes

### ☁️ AWS ECR

```bash
# Pull from AWS ECR  
docker pull public.ecr.aws/cortexai/cortex:latest

# Run locally
docker run -p 8080:8080 \
  -e CO_API_KEY="your-key" \
  public.ecr.aws/cortexai/cortex:latest
```

### 📦 Local Development
```bash
# Install with correct psycopg package
pip install psycopg[binary]==3.2.9  # Important: Use psycopg[binary], not psycopg-binary
pip install cortex
```

### 🔨 Build & Push to Docker Hub

**Build the production image:**
```bash
# Build optimized Lambda-compatible image
# IMPORTANT: Use --platform linux/amd64 and --provenance=false for Lambda compatibility
docker build --platform linux/amd64 --provenance=false -f Dockerfile.lambda.full -t cortex-api .

# Test locally first
docker run -p 8080:8080 \
  -e CO_API_KEY="your-key" \
  cortex-api
```

**Push to Docker Hub:**
```bash
# Login to Docker Hub
docker login

# Tag for Docker Hub (replace 'yourusername' with your Docker Hub username)
docker tag cortex-api:latest yourusername/cortex-api:latest

# Push to Docker Hub
docker push yourusername/cortex-api:latest

# Your image is now available at:
# docker pull yourusername/cortex-api:latest
```

### 🔨 Build & Push to AWS ECR

**Setup ECR repository:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name cortex-api --region us-east-1

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [account-id].dkr.ecr.us-east-1.amazonaws.com
```

**Build and push:**
```bash
# Build the image with Lambda-compatible architecture
docker build --platform linux/amd64 --provenance=false -f Dockerfile.lambda.full -t cortex-api .

# Tag for ECR
docker tag cortex-api:latest [account-id].dkr.ecr.us-east-1.amazonaws.com/cortex-api:latest

# Push to ECR
docker push [account-id].dkr.ecr.us-east-1.amazonaws.com/cortex-api:latest
```

## Usage

### Basic Usage
```python
from cortex.responses import ResponsesAPI

# Initialize with optional database
api = ResponsesAPI(db_url="postgresql://user:pass@host:5432/db")

# Create a response
response = api.create(
    input="Explain quantum computing",
    model="gpt-4o",
    instructions="You are a physics expert",
    store=True,  # Enable persistence
    temperature=0.7
)

print(response["message"]["content"])
```

### Continue Conversation
```python
# Continue previous conversation
response2 = api.create(
    input="Can you explain quantum entanglement?",
    model="gemini-1.5-pro",  # Switch models mid-conversation
    previous_response_id=response["id"],
    store=True
)
```

## Parameters

### Required
- **input**: User's message (string)
- **model**: LLM model identifier (string)

### Optional
- **db_url**: Database connection string (overrides instance default)
- **previous_response_id**: Continue previous conversation (string)
- **instructions**: System instructions for assistant (string)
- **store**: Enable conversation persistence (boolean, default: True)
- **temperature**: LLM temperature 0.0-2.0 (float, default: 0.7)
- **metadata**: Additional metadata to store (dict)

## Best Practices

### Do's
- Always use `store=True` with PostgreSQL/Supabase poolers
- Set appropriate temperature for your use case
- Use `previous_response_id` for conversation continuity
- Handle potential glitches with try-catch blocks

### Don'ts  
- Don't assume streaming support
- Don't use very high temperatures (>1.5) without testing
- Don't rely on tool calling functionality yet
- Don't ignore database connection errors

## Deployment Guide

### 🏠 Local Development

**Step 1: Install Cortex**
```bash
pip install cortex
```

**Step 2: Set environment variables**
```bash
export CO_API_KEY="your-cohere-key"
export OPENAI_API_KEY="your-openai-key" 
export GOOGLE_API_KEY="your-google-key"
export DATABASE_URL="postgresql://user:pass@host:5432/db"  # Optional
```

**Step 3: Create your application**
```python
# app.py
from cortex.responses import ResponsesAPI

# Initialize API
api = ResponsesAPI()

# Create response
response = api.create(
    input="Hello, how are you?",
    model="command-r",
    instructions="You are a helpful assistant"
)

print(response["message"]["content"])
```

**Step 4: Run**
```bash
python app.py
```

### ☁️ Serverless Deployment (AWS Lambda)

#### Option 1: Use Docker Hub Image (Fastest - Recommended!)
```bash
# First, pull and tag the image for Lambda
docker pull reaper27/cortex-api:latest
docker tag reaper27/cortex-api:latest [account-id].dkr.ecr.[region].amazonaws.com/cortex:latest

# Push to your ECR
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [account-id].dkr.ecr.[region].amazonaws.com
docker push [account-id].dkr.ecr.[region].amazonaws.com/cortex:latest

# Deploy Lambda function
aws lambda create-function \
  --function-name cortex-api \
  --code ImageUri=[account-id].dkr.ecr.[region].amazonaws.com/cortex:latest \
  --role arn:aws:iam::account:role/lambda-role \
  --package-type Image \
  --memory-size 512 \
  --timeout 30 \
  --environment Variables='{
    "CO_API_KEY":"your-cohere-key",
    "OPENAI_API_KEY":"your-openai-key",
    "GOOGLE_API_KEY":"your-google-key",
    "DATABASE_URL":"postgresql://..."
  }'
```

#### Option 2: Use AWS ECR Image
```bash
# Deploy using ECR image
aws lambda create-function \
  --function-name cortex-api \
  --code ImageUri=public.ecr.aws/cortexai/cortex:latest \
  --role arn:aws:iam::account:role/lambda-role \
  --package-type Image
```

#### Option 3: Build Locally & Deploy

**Step 1: Customize Dockerfile.lambda.full**
```dockerfile
# Dockerfile.lambda.full (already included)
FROM public.ecr.aws/lambda/python:3.11 AS builder
# ... optimized multi-stage build
COPY cortex/ ${LAMBDA_TASK_ROOT}/cortex/
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}/
CMD ["lambda_handler.lambda_handler"]
```

**Step 2: Build and push**
```bash
# Build image with correct architecture flags
# --platform linux/amd64: Ensures Lambda-compatible architecture
# --provenance=false: Prevents attestation issues with Lambda
docker build --platform linux/amd64 --provenance=false -f Dockerfile.lambda.full -t cortex-lambda .

# Tag for ECR
docker tag cortex-lambda:latest 123456789012.dkr.ecr.region.amazonaws.com/cortex:latest

# Push to ECR
docker push 123456789012.dkr.ecr.region.amazonaws.com/cortex:latest
```

**Step 3: Deploy Lambda**
```bash
aws lambda create-function \
  --function-name cortex-api \
  --code ImageUri=123456789012.dkr.ecr.region.amazonaws.com/cortex:latest \
  --role arn:aws:iam::account:role/lambda-role \
  --package-type Image
```

### 🚀 Production Examples

#### Flask Backend Integration
```python
# flask_app.py
from flask import Flask, request, jsonify
from cortex.responses import ResponsesAPI

app = Flask(__name__)
api = ResponsesAPI(db_url="postgresql://user:pass@host:5432/db")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    
    response = api.create(
        input=data['message'],
        model=data.get('model', 'command-r'),
        previous_response_id=data.get('conversation_id'),
        instructions=data.get('system_prompt'),
        store=True,
        temperature=data.get('temperature', 0.7)
    )
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### FastAPI Backend Integration  
```python
# fastapi_app.py
from fastapi import FastAPI
from pydantic import BaseModel
from cortex.responses import ResponsesAPI

app = FastAPI()
api = ResponsesAPI()

class ChatRequest(BaseModel):
    message: str
    model: str = "command-r"
    conversation_id: str = None
    system_prompt: str = None
    temperature: float = 0.7

@app.post("/chat")
async def chat(request: ChatRequest):
    response = api.create(
        input=request.message,
        model=request.model,
        previous_response_id=request.conversation_id,
        instructions=request.system_prompt,
        store=True,
        temperature=request.temperature
    )
    return response
```

#### Docker Production Setup
```bash
# Using Docker Hub image in production
docker run -d \
  --name cortex-api \
  -p 8080:8080 \
  --restart unless-stopped \
  -e CO_API_KEY="your-cohere-key" \
  -e OPENAI_API_KEY="your-openai-key" \
  -e DATABASE_URL="postgresql://user:pass@supabase:5432/postgres" \
  reaper27/cortex-api:latest
```

**Image Details:**
- 🏷️ **Tag**: `reaper27/cortex-api:latest`
- 📏 **Size**: 317MB compressed (optimized multi-stage build)
- 🏗️ **Architecture**: linux/amd64 (Lambda-compatible)
- ⏰ **Last Updated**: December 2024
- ✅ **Includes**: All recent fixes for pooler compatibility, GSSAPI, and model updates
- 🔧 **Base**: AWS Lambda Python 3.11 runtime

## Environment Variables

Set API keys for the providers you want to use:
- `OPENAI_API_KEY`: OpenAI models
- `GOOGLE_API_KEY`: Google Gemini models  
- `CO_API_KEY`: Cohere models
- `DATABASE_URL`: PostgreSQL connection string

## Response Format

Cortex returns OpenAI-compatible response format:
```json
{
  "id": "response_abc123",
  "object": "response",
  "created": 1699000000,
  "model": "gpt-4o",
  "message": {
    "role": "assistant", 
    "content": "Response content here..."
  },
  "usage": {
    "total_tokens": 150,
    "completion_tokens": 100,
    "prompt_tokens": 50
  }
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Connection pooler temporarily unstable" Error
**Problem**: Getting pipeline mode errors with Supabase or other pooled connections  
**Solution**: The system will automatically retry. If persistent:
- Cortex automatically detects and handles pooler instability
- Error messages include the response_id to maintain conversation continuity
- Simply retry the request - the system handles recovery gracefully

#### 2. GSSAPI Authentication Errors in Lambda
**Problem**: `'PGconn' object has no attribute 'used_gssapi'` error  
**Solution**: 
- Ensure you're using `psycopg[binary]==3.2.9` NOT `psycopg-binary`
- The system automatically disables GSSAPI for Lambda compatibility
- Rebuild your Docker image with the correct package

#### 3. "Current transaction is aborted" on Fresh Databases
**Problem**: First request to a new database fails with transaction errors  
**Solution**:
- Cortex handles this automatically with autocommit for setup operations
- The system creates necessary tables and checkpoints on first use
- Retry the request if you encounter this error

#### 4. Model Not Found (404) Errors
**Problem**: Gemini or Cohere models returning 404 errors  
**Solution**:
- Check the supported models list above for current model names
- Google deprecated `gemini-1.5-flash`, use `gemini-2.0-flash` instead
- Some Cohere models have been deprecated - use `command-r` or `command-r-plus`

#### 5. Lambda Deployment Issues
**Problem**: Lambda function fails to start or crashes  
**Solution**:
```bash
# Ensure PostgreSQL libraries are included
# The Dockerfile.lambda.full already includes:
RUN yum install -y postgresql-libs && yum clean all

# Verify correct package in requirements-lambda.txt:
psycopg[binary]==3.2.9  # NOT psycopg-binary
```

#### 6. Connection Pooler Detection
**Problem**: Not sure if Cortex is detecting your pooled connection  
**Solution**:
- Cortex automatically detects Supabase and pgBouncer connections
- Check logs for "Pooled connection detected" message
- The system applies appropriate handling automatically

### Quick Fixes Checklist

✅ **For Fresh Deployments:**
1. Use the Docker Hub image: `reaper27/cortex-api:latest`
2. Set all required environment variables
3. Ensure DATABASE_URL uses the pooler port (6543 for Supabase)
4. First request may need a retry due to table creation

✅ **For Lambda Issues:**
1. Use `Dockerfile.lambda.full` for building
2. Build with `--platform linux/amd64 --provenance=false` flags
3. Verify `psycopg[binary]` package (not `psycopg-binary`)
4. Check Lambda has sufficient memory (512MB minimum)
5. Ensure timeout is set to at least 30 seconds

✅ **For Model Issues:**
1. Use the latest model names from the supported list
2. Ensure API keys are correctly set for each provider
3. Check provider service status if errors persist

## Contributing

Cortex is in active development. We welcome contributions, bug reports, and feature requests.
