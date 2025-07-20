# PassManager-Server
The Server-Side implementation of the password manager.


## APIs

This application supports REST APIs.

### Base URL
- **Development/Testing**: `https://127.0.0.1:5000` (local access only)
- **Production**: `https://0.0.0.0:5000` (network accessible)

**Note**: The server uses self-signed certificates for development. You may see security warnings in browsers - this is normal and expected for development environments.

### API Structure

API endpoints follow the pattern: `/api/{type}/{callName}`

Where:
- `{type}` can be: `user`, `session`, `data`
- `{callName}` is the specific endpoint name

#### Request Methods

- **GET requests**: Used for retrieving data (e.g., health checks)
- **POST requests**: Used for sending data securely in the request body (JSON format)

### API Testing

Example curl commands:

```bash
# Health check (GET)
curl -k https://127.0.0.1:5000/api/user/health

# Hello world test (POST with empty body)
curl -k -X POST https://127.0.0.1:5000/api/user/hello

# Hello with custom message (POST with JSON body)
curl -k -X POST https://127.0.0.1:5000/api/user/hello \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from README"}'

# Hello with multiple arguments (POST with JSON body)
curl -k -X POST https://127.0.0.1:5000/api/user/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "age": 25, "city": "New York"}'
```


## Testing

Testing is done automatically through Github CI when merging (or pushing) into the branch 'main'.

### How It Works

This uses:
- Ubuntu-latest
- Python 3.11
- requirements.txt

And runs all tests in the tests directory.

### Running Tests Locally

To run all tests locally:

```bash
# Create virtual environment
python -m venv env
# Enter env
env\Scripts\activate        # Windows
source env/bin/activate     # Other systems
# Install dependencies
pip install -r requirements.txt
# Run all tests
python -m pytest tests/ -v
```

Alternatively, running one of the test files as a python file will run all tests within that suite.
