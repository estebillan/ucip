# FastAPI Dependency Injection Comprehensive Guide

## Key Concepts of Dependency Injection in FastAPI:

### 1. Definition
- "Dependency Injection" means declaring things your code requires to work
- FastAPI automatically handles providing ("injecting") those dependencies

### 2. Basic Structure
- Dependencies are functions that can take the same parameters as path operation functions
- Use `Depends()` to declare dependencies in function parameters
- Can be synchronous (`def`) or asynchronous (`async def`)

### 3. Simple Example
```python
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

### 4. Key Benefits
- Minimize code repetition
- Share database connections
- Enforce security and authentication
- Integrate external components easily

### 5. Advanced Features
- Dependencies can have sub-dependencies
- Supports complex hierarchical dependency trees
- Fully integrated with OpenAPI documentation
- Compatible with various databases, authentication systems, and external APIs

### 6. Best Practices
- Prefer `Annotated` for type hints
- Use type aliases for reusable dependencies
- Keep dependencies modular and focused

The system is designed to be "Simple and Powerful", allowing complex integrations with minimal boilerplate code.