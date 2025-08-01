# FastAPI Async Programming Comprehensive Guide

## Key Async Concepts:
### 1. Asynchronous Code Basics
- Allows the program to do other work while waiting for I/O operations
- Primarily useful for network, database, file system, and API interactions
- Enables more efficient handling of "waiting" time during operations

### 2. Concurrency vs Parallelism
- Concurrency: Switching between tasks during waiting periods
- Parallelism: Simultaneously executing multiple tasks on different processors
- Web applications benefit more from concurrency due to frequent waiting periods

### 3. When to Use `async def`:
- Use `async def` when working with libraries that support `await`
- Example: 
```python
@app.get('/burgers')
async def read_burgers():
    burgers = await get_burgers(2)
    return burgers
```

### 4. When to Use Regular `def`:
- Use regular `def` for:
  - Libraries without `await` support
  - Database interactions without async libraries
  - Simple computational tasks

### 5. Best Practices:
- If unsure, default to regular `def`
- Mix `async def` and `def` as needed in your application
- FastAPI will optimize performance automatically

### 6. Performance Considerations:
- Async code is particularly effective for I/O-bound tasks
- Provides high performance comparable to Go and NodeJS
- Supports both web development concurrency and parallel processing for machine learning

## Practical Tip: 
"If you are using third party libraries that tell you to call them with `await`, declare your path operation functions with `async def`."