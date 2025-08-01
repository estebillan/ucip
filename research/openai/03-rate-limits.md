# OpenAI Rate Limits Comprehensive Guide

## Rate Limit Types:
1. **Requests Per Minute (RPM)**: Number of requests per minute
2. **Tokens Per Minute (TPM)**: Number of tokens per minute
3. **Tokens Per Day (TPD)**: Number of tokens per day

## Model-Specific Limits (Tier 1):
- **GPT-4**: 20 RPM, 30K TPM
- **GPT-3.5-turbo**: 60 RPM, 90K TPM
- **GPT-4-turbo**: 20 RPM, 30K TPM

## Rate Limit Headers:
```python
response = client.chat.completions.create(...)
print(response.headers.get('x-ratelimit-remaining-requests'))
print(response.headers.get('x-ratelimit-remaining-tokens'))
print(response.headers.get('x-ratelimit-reset-requests'))
print(response.headers.get('x-ratelimit-reset-tokens'))
```

## Handling Rate Limits:
```python
import time
from openai import RateLimitError

def make_request_with_retry(client, **kwargs):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

## Best Practices:
1. **Implement Exponential Backoff**: Wait progressively longer between retries
2. **Track Usage**: Monitor token consumption
3. **Batch Requests**: Group multiple operations when possible
4. **Use Appropriate Models**: GPT-3.5-turbo for simpler tasks
5. **Cache Results**: Avoid duplicate API calls
6. **Request Limit Increases**: Contact OpenAI for higher limits

## Token Estimation:
```python
import tiktoken

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Estimate before making request
token_count = count_tokens("Your prompt here")
```

## Production Rate Limiting:
```python
import asyncio
import aiohttp
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, max_requests_per_minute=20):
        self.semaphore = Semaphore(max_requests_per_minute)
        self.requests = []
    
    async def acquire(self):
        await self.semaphore.acquire()
        # Track request timing for sliding window
        current_time = time.time()
        self.requests.append(current_time)
        
        # Clean old requests
        self.requests = [req for req in self.requests if current_time - req < 60]
        
        if len(self.requests) >= 20:
            sleep_time = 60 - (current_time - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
```