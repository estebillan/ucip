# OpenAI Chat Completions API Comprehensive Guide

## Basic Chat Completions Usage
```python
import openai
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
```

## Key Parameters:
- **model**: "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"
- **messages**: Array of message objects with role and content
- **max_tokens**: Maximum tokens in response
- **temperature**: 0-2, controls randomness
- **top_p**: Alternative to temperature for nucleus sampling
- **frequency_penalty**: -2.0 to 2.0, penalizes repetition
- **presence_penalty**: -2.0 to 2.0, encourages new topics

## Message Roles:
- **system**: Sets behavior/context for assistant
- **user**: User input/questions
- **assistant**: AI responses
- **function**: Function call results (deprecated, use tools)

## Response Format:
```python
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help you today?"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
    }
}
```

## Streaming Support:
```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## Error Handling:
- **RateLimitError**: Too many requests
- **APIConnectionError**: Network issues
- **AuthenticationError**: Invalid API key
- **InvalidRequestError**: Malformed request