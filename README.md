# Cortex - OpenAI Responses API Alternative

**🚨 Beta Status**: Cortex is currently in beta. While functional, it may have glitches and is actively being developed.

Cortex is a powerful Python framework that replicates OpenAI's Responses API functionality with multi-provider LLM support, advanced conversation persistence, and both local and serverless deployment capabilities.

## Why Cortex?

### Advantages Over OpenAI Responses API
- **Multi-Provider Support**: Use OpenAI, Google Gemini, Cohere, and Anthropic models seamlessly
- **Cost Effective**: Access to free and cheaper LLM alternatives 
- **Cross-Model Conversations**: Switch models mid-conversation while maintaining context
- **Flexible Deployment**: Local development, Docker containers, and serverless (AWS Lambda)
- **Advanced Persistence**: Sophisticated checkpointing system with PostgreSQL and SQLite support
- **Pooler Compatible**: Works with connection poolers like Supabase with proper threading locks
- **Open Source**: Full control and transparency

### Current Limitations
- **No Streaming**: Responses are returned as complete messages only
- **No Tool Calling**: Function/tool calling not yet implemented
- **Beta Stability**: May have occasional glitches, especially with pooler connections

## Architecture

Cortex uses a sophisticated checkpointing system for conversation persistence:

- **persistence.py**: Advanced connection pooler detection with threading locks for concurrent access
- **create.py**: Handles initial conversation state and instructions persistence following OpenAI spec  
- **api.py**: Core orchestration with error handling and LLM invocation
- **models/registry.py**: Multi-provider model configurations and deprecation management

The system automatically detects connection poolers (like Supabase) and applies appropriate threading locks to prevent pipeline mode conflicts.

## Supported Models

### OpenAI
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`

### Google Gemini  
- `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-1.0-pro`

### Cohere
- `command-r`, `command-r-plus`, `command`


## Database Support

- **PostgreSQL**: Full production support with connection pooler compatibility
- **SQLite**: Local development and testing
- **MemorySaver**: In-memory conversations (non-persistent)

## Installation & Deployment

### 🐳 Docker Hub (Recommended)

**Pre-built images available on Docker Hub for instant deployment:**

🔗 **Docker Hub Repository**: https://hub.docker.com/repository/docker/reaper27/cortex-api

```bash
# Pull from Docker Hub (317MB compressed)
docker pull reaper27/cortex-api:latest

# Run locally
docker run -p 8080:8080 \
  -e CO_API_KEY="your-cohere-key" \
  -e DATABASE_URL="postgresql://..." \
  reaper27/cortex-api:latest
```

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
pip install cortex
```

### 🔨 Build Locally
```bash
docker build -f Dockerfile.lambda.full -t cortex .
docker run -p 8080:8080 cortex
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

#### Option 1: Use Docker Hub Image (Fastest)
```bash
# Deploy using pre-built image from Docker Hub
aws lambda create-function \
  --function-name cortex-api \
  --code ImageUri=reaper27/cortex-api:latest \
  --role arn:aws:iam::account:role/lambda-role \
  --package-type Image \
  --environment Variables='{
    "CO_API_KEY":"your-key",
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
# Build image
docker build -f Dockerfile.lambda.full -t cortex-lambda .

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
- 📏 **Size**: 317MB compressed
- 🏗️ **Architecture**: linux/amd64
- ⏰ **Last Updated**: Updated regularly
- 📋 **Digest**: `sha256:be1c7159c7f5a054c57161cc8b6f80a5dce6e9a4eba76edc3c42a1dc1db37e18`

## Environment Variables

Set API keys for the providers you want to use:
- `OPENAI_API_KEY`: OpenAI models
- `GOOGLE_API_KEY`: Google Gemini models  
- `CO_API_KEY`: Cohere models
- `ANTHROPIC_API_KEY`: Anthropic models
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

## Contributing

Cortex is in active development. We welcome contributions, bug reports, and feature requests.

## License

MIT License - see LICENSE file for details.
