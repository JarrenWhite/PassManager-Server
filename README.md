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
├── config/
│   ├── config.ini
│   └── logging_config.json
│
├── PassManager-Protobufs/
│
├── docs/
│
├── src/
│   ├── main.py
│   │
│   ├── cryptography/
│   ├── database/
│   ├── enums/
│   ├── passmanager/
│   ├── services/
│   └── utils/
│
└── tests/
```
