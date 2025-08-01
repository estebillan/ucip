# FastAPI File Uploads Comprehensive Guide

## Key File Upload Techniques:
### 1. Basic File Upload
- Use `File()` and `UploadFile` imports from FastAPI
- Can upload files as `bytes` or `UploadFile` objects
- Requires `python-multipart` package installation

### 2. File Upload Advantages with `UploadFile`:
- Handles large files efficiently
- Uses "spooled" file storage (memory/disk)
- Provides file metadata (filename, content type)
- Supports async file-like operations

### 3. Multiple File Upload Patterns:
- Upload lists of files using `list[bytes]` or `list[UploadFile]`
- Support optional file uploads with `None` default
- Add metadata using `File(description="...")`

## Example Basic Upload:
```python
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
```

## Key `UploadFile` Methods:
- `write(data)`
- `read(size)`
- `seek(offset)`
- `close()`

## Important Considerations:
- Files sent as "form data"
- Can't combine file uploads with JSON body
- Use async methods with `await`