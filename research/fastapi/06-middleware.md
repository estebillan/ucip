# FastAPI Middleware Comprehensive Guide

## Key Middleware Characteristics:
- A middleware is a function that processes every request before path operations
- It can modify requests before processing and responses before returning
- Middleware runs for every request in the application

## Creating a Middleware:
- Use the `@app.middleware("http")` decorator
- The middleware function receives:
  1. The request
  2. A `call_next` function to pass the request to path operations

## Example Middleware:
```python
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Middleware Execution Order:
- Middlewares are stacked, with the last added being the outermost
- Request flow: Outermost middleware → Innermost middleware → Route
- Response flow: Route → Innermost middleware → Outermost middleware

## Additional Notes:
- Middleware can run code before and after response generation
- More advanced middleware techniques are covered in the Advanced User Guide
- The next section will discuss CORS middleware specifically