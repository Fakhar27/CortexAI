# Cortex - Open Source Alternative to OpenAI APIs

Cortex is a Python framework that provides OpenAI-compatible APIs using free LLMs and LangGraph.

## Features

- 🚀 **Responses API** - Simple conversation API like OpenAI
- 🆓 **Free LLMs** - Uses Cohere instead of expensive OpenAI
- 💾 **Conversation Persistence** - Built-in conversation memory
- 🎯 **Simple to Use** - Hide LangGraph complexity

## Installation

```bash
pip install cortex
```

## Quick Start

```python
from cortex import ResponsesAPI

# Initialize the API
api = ResponsesAPI(llm_provider="cohere")

# Create a response
response = api.create(
    input="Tell me about Python",
    instructions="You are a helpful programming tutor"
)

print(response["message"]["content"])

# Continue the conversation
response2 = api.create(
    input="What about decorators?",
    previous_response_id=response["conversation_id"]
)
```

## Next.js Integration

```javascript
// pages/api/chat.js
export default async function handler(req, res) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req.body)
  });
  
  const data = await response.json();
  res.status(200).json(data);
}
```

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Format code
black cortex/
```

## License

MIT
