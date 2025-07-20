# PassManager-Server
The Server-Side implementation of the password manager.



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
