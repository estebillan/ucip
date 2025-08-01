# FastAPI Background Tasks

## Overview
Background Tasks in FastAPI allow you to perform operations after sending a response, which is useful for:
- Email notifications
- Processing data
- Logging  
- Other tasks that don't require immediate completion

## Key Features:
1. Import `BackgroundTasks` from FastAPI
2. Create a task function (can be async or sync)
3. Add tasks using `.add_task()` method

## Example Usage:
```python
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

## Important Considerations:
- Works with dependency injection
- Supports multiple background tasks
- Best for lightweight background operations

## Caveat: 
"If you need to perform heavy background computation... you might benefit from using other bigger tools like Celery."