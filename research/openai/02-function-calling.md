# OpenAI Function Calling Comprehensive Guide

## Function Calling Overview
Function calling allows models to intelligently choose when to call functions and extract structured data.

## Basic Function Definition:
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

## Function Calling Request:
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What's the weather in Boston?"}
    ],
    tools=tools,
    tool_choice="auto"  # "auto", "none", or {"type": "function", "function": {"name": "function_name"}}
)
```

## Handling Function Calls:
```python
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    # Call your function
    result = get_weather(**function_args)
    
    # Send result back to model
    messages.append(response.choices[0].message)
    messages.append({
        "tool_call_id": tool_call.id,
        "role": "tool",
        "content": str(result)
    })
```

## Parallel Function Calling:
Models can call multiple functions simultaneously:
```python
# Model might call multiple functions in one response
for tool_call in response.choices[0].message.tool_calls:
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    # Process each function call
```

## Best Practices:
- Use clear function descriptions
- Define required vs optional parameters
- Validate function arguments
- Handle function errors gracefully
- Use enum for limited choice parameters
- Keep function responses concise but informative