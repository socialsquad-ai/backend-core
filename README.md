# Project Setup

## Prerequisites
- **PostgreSQL**: Version 16.6 or higher
- **Python**: Version 3.12 or higher

## Setup Instructions

1. **Start PostgreSQL Server**  
   Ensure PostgreSQL (min version 16.6) is running.

2. **Run Initial SQL Setup**  
   Execute the SQL script located at:
   ```sh
   data_adapter/sql-postgres/1.initial_setup.sql
   ```

3. **Create a Virtual Environment**  
   In the project root directory, create a virtual environment:
   ```sh
   python3.12 -m venv .venv
   ```

4. **Activate the Virtual Environment**  
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

5. **Install Dependencies**  
   Run the following command to install required packages:
   ```sh
   pip install -r requirements.txt
   ```

6. **Run the Application**  
   Use the predefined launch configuration in the `.vscode` folder to run the application. Or use
   ```sh
   uvicorn server.app:app --reload --host 0.0.0.0 --port 8000   
   ```



## Endpoint Execution Order

In our FastAPI application, the execution order of decorators in controller functions follows a **top-to-bottom** approach.

### **Decorator Execution Flow**
1. **`@require_authentication`** → Runs first to validate authentication.
2. **`@validate_payload`** → Runs after authentication to validate the request payload.

#### **Example:**
```python
@require_authentication
@validate_payload({
        "key" : {"type" : "string", "required" : True}
})
async def example_endpoint(request: Request):
    # Function logic executes after authentication & validation
    return {"message": "Success"}

```

## Background Tasks with Context Preservation

The application includes a custom background task system that preserves request context variables across different threads/coroutines.

### **How It Works**

The `@run_in_background` decorator allows you to run functions in the background while maintaining access to request metadata and context variables. This is particularly useful for:

- Long-running tasks that shouldn't block the API response
- Tasks that need access to request context (api_id, thread_id, etc.)
- Background processing that requires the same request context as the main request

### **Key Features**

1. **Context Preservation**: Copies request metadata from the main coroutine to the background task
2. **Thread ID Generation**: Creates a new unique `thread_id` for each background task while preserving the original `api_id`
3. **Thread Safety**: Uses ThreadPoolExecutor for safe concurrent execution
4. **Async Support**: Works with both synchronous and asynchronous functions

### **Usage Example**

```python
from decorators.common import run_in_background
from utils.contextvar import get_request_metadata

@run_in_background
def background_job():
    import time
    
    # Access request metadata in the background task
    metadata = get_request_metadata()
    print(f"Background job running with metadata: {metadata}")
    
    count = 0
    while True:
        time.sleep(1)
        count += 1
        print(f"Background job running for seconds: {count}")

# In your usecase or controller:
def some_business_logic():
    # Trigger background job
    background_job()
    # Main logic continues without waiting for background job
    return "Task started in background"
```

### **Metadata Behavior**

When using `@run_in_background`, the metadata context behaves as follows:

| Context | `api_id` | `thread_id` | Description |
|---------|----------|-------------|-------------|
| Main Request | `abc-123` | `def-456` | Original request context |
| Background Task | `abc-123` | `ghi-789` | Same API ID, new thread ID |

### **Important Notes**

- **Non-blocking**: Background tasks run independently and don't block the main request response
- **Context Isolation**: Each background task gets its own `thread_id` while sharing the same `api_id`
- **Thread Safety**: Uses ThreadPoolExecutor with configurable worker count
- **Error Handling**: Background task errors don't affect the main request response

### **Configuration**

The background task system uses a ThreadPoolExecutor with configurable settings:

```python
# In decorators/common.py
executor = ThreadPoolExecutor(max_workers=4)  # Adjust based on your needs
```

### **Best Practices**

1. **Use for Long-Running Tasks**: Perfect for tasks that take more than a few seconds
2. **Preserve Context**: Ideal when you need request metadata in background processing
3. **Error Handling**: Implement proper error handling within your background functions
4. **Resource Management**: Be mindful of the number of concurrent background tasks
