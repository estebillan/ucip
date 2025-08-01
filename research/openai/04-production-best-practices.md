# OpenAI Production Best Practices

## Security Best Practices:
1. **API Key Management**:
   - Store API keys as environment variables
   - Never commit keys to version control
   - Use different keys for different environments
   - Rotate keys regularly

2. **Input Validation**:
   - Sanitize user inputs
   - Implement content filtering
   - Set maximum input lengths
   - Validate data types

## Error Handling:
```python
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def make_openai_request(client, **kwargs):
    try:
        return await client.chat.completions.create(**kwargs)
    except openai.RateLimitError:
        # Handle rate limits with exponential backoff
        raise
    except openai.APIConnectionError:
        # Handle connection errors
        raise
    except openai.AuthenticationError:
        # Handle authentication errors
        logger.error("Invalid API key")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

## Monitoring and Logging:
```python
import structlog
import time

logger = structlog.get_logger(__name__)

def log_openai_request(model, prompt_tokens, completion_tokens, cost):
    logger.info(
        "OpenAI API request completed",
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        estimated_cost=cost,
        timestamp=time.time()
    )
```

## Cost Optimization:
1. **Model Selection**:
   - Use GPT-3.5-turbo for simpler tasks
   - Use GPT-4 only when necessary
   - Consider fine-tuned models for specific use cases

2. **Token Management**:
   - Implement token counting
   - Truncate long inputs intelligently
   - Cache frequent responses

3. **Usage Tracking**:
```python
class UsageTracker:
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0
        self.requests = []
    
    def track_usage(self, model, prompt_tokens, completion_tokens):
        total = prompt_tokens + completion_tokens
        self.total_tokens += total
        
        # Cost calculation (example rates)
        if model == "gpt-4":
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
        elif model == "gpt-3.5-turbo":
            cost = (prompt_tokens * 0.001 + completion_tokens * 0.002) / 1000
        
        self.total_cost += cost
        self.requests.append({
            "timestamp": time.time(),
            "model": model,
            "tokens": total,
            "cost": cost
        })
```

## Performance Optimization:
1. **Async Operations**:
```python
import asyncio
from openai import AsyncOpenAI

async def process_multiple_requests(prompts):
    client = AsyncOpenAI()
    tasks = []
    
    for prompt in prompts:
        task = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

2. **Connection Pooling**:
```python
import aiohttp
from openai import AsyncOpenAI

# Configure HTTP client with connection pooling
connector = aiohttp.TCPConnector(
    limit=100,  # Total connection pool size
    limit_per_host=30,  # Connections per host
    ttl_dns_cache=300,  # DNS cache TTL
)

client = AsyncOpenAI(
    http_client=aiohttp.ClientSession(connector=connector)
)
```

## Testing Strategies:
1. **Mock Testing**:
```python
import pytest
from unittest.mock import Mock, patch

@patch('openai.AsyncOpenAI')
def test_content_generation(mock_openai):
    mock_response = Mock()
    mock_response.choices[0].message.content = "Test response"
    mock_openai.return_value.chat.completions.create.return_value = mock_response
    
    # Test your function
    result = generate_content("test prompt")
    assert result == "Test response"
```

2. **Integration Testing**:
- Use test API keys with lower rate limits
- Test error scenarios (invalid inputs, rate limits)
- Validate response formats and content quality