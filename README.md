# PassManager-Server
The Server-Side implementation of the password manager.


## APIs

This application supports REST APIs.

### Base URL
- **Development/Testing**: `http://127.0.0.1:5000` (local access only)
- **Production**: `http://0.0.0.0:5000` (network accessible)

### API Structure

API endpoints follow the pattern: `/api/{type}/{callName}`

Where:
- `{type}` can be: `user`, `session`, `data`
- `{callName}` is the specific endpoint name

#### Query Parameters

Many endpoints accept query parameters for additional functionality:

- **GET requests**: Use query parameters in the URL (e.g., `?param1=value1&param2=value2`)
- **Parameters are optional** unless specified otherwise
- **URL encoding** is required for special characters (spaces become `%20`, etc.)

### API Testing

Example curl commands:

```bash
# Health check
curl http://127.0.0.1:5000/api/user/health

# Hello world test
curl http://127.0.0.1:5000/api/user/hello

# Hello with custom message
curl "http://127.0.0.1:5000/api/user/hello?message=Hello%20from%20README"

# Hello with multiple arguments
curl "http://127.0.0.1:5000/api/user/hello?name=John&age=25&city=New%20York"
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
