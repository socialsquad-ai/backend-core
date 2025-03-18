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
