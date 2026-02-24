# Pass Manager Server

Lightweight server deployment for a password manager utilising trust free architecture.
Intended to be deployable using small scale infrastructure, without compromising on security.


## Documentation
1. [Cryptographic Implementation](docs/cryptographic_implementation.md) - Details on encryption algorithms, key management, and security protocols used in the password manager
2. [Authentication](docs/authentication.md) - User authentication methods, session management, and access control mechanisms
3. [Database Schema](docs/database_schema.md) - Database structure, table definitions, and relationships for storing encrypted password data
4. [API Calls](docs/api_calls.md) - Complete API endpoint documentation with request formats, parameters, and usage examples
5. [API Responses](docs/api_responses.md) - Standard response formats, error codes, and data structures returned by the API


## Protobuf & gRPC
The protobuf and RPC definitions can be found [here](https://github.com/JarrenWhite/PassManager-Protobufs).

These definitions are used for all calls to or from the server.


## Tests
Each completed implementation file has an associated test file. . Each function is tested within that test file. The test file name is determined by the implementation file's package and filename, following the format `test_[package]_[filename].py`.

The tests make use of the pytest framework. As well as being runnable using a pytest command, each test file has been configured to run all tests if being run in standard python. Additionally, the `all_tests.py` file has been configured to run all tests if run in standard python.


## File Structure

```
/
├── README.md
├── requirements.txt
│
├── config
│   ├── config.ini
│   └── logging_config.json
│
├── PassManager-Protobufs
│
├── docs
│   ├── api_calls.md
│   ├── api_responses.md
│   ├── authentication.md
│   ├── cryptographic_implementation.md
│   ├── database_schema.md
│   │
│   └── design
│       ├── api_call_lifecycle.md
│       ├── cryptography_utils.md
│       ├── db_utils.md
│       ├── PassManager-Server.pdf
│       └── password_change_lifecycle.md
│
├── src
│   ├── main.py
│   │
│   ├── database
│   │   ├── __init__.py
│   │   ├── database_models.py
│   │   └── database_setup.py
│   │
│   ├── enums
│   │   ├── __init__.py
│   │   └── failure_reason.py
│   │
│   └── utils
│       ├── __init__.py
│       ├── database_config.py
│       ├── db_utils_auth.py
│       ├── db_utils_data.py
│       ├── db_utils_password.py
│       ├── db_utils_session.py
│       ├── db_utils_user.py
│       ├── logging_setup.py
│       ├── service_utils.py
│       └── session_manager.py
│
└── tests
    ├── all_tests.py
    ├── mock_classes.py
    ├── test_database_database_models.py
    ├── test_database_database_setup.py
    ├── test_utils_database_config.py
    ├── test_utils_db_utils_auth.py
    ├── test_utils_db_utils_data.py
    ├── test_utils_db_utils_password.py
    ├── test_utils_db_utils_session.py
    └── test_utils_db_utils_user.py
```
