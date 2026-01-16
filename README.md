# Pass Manager Server

Lightweight server deployment for a password manager utilising trust free architecture.
Intended to be deployable using small scale infrastructure, without compromising on security.

## Documentation
1. [Cryptographic Implementation](docs/cryptographic_implementation.md) - Details on encryption algorithms, key management, and security protocols used in the password manager
2. [Authentication](docs/authentication.md) - User authentication methods, session management, and access control mechanisms
3. [Database Schema](docs/database_schema.md) - Database structure, table definitions, and relationships for storing encrypted password data
4. [API Calls](docs/api_calls.md) - Complete API endpoint documentation with request formats, parameters, and usage examples
5. [API Responses](docs/api_responses.md) - Standard response formats, error codes, and data structures returned by the API


## Tests


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
├── docs
│   ├── design
│   │   ├── api_call_lifecycle.md
│   │   ├── cryptography_utils.md
│   │   ├── db_utils.md
│   │   ├── PassManager-Server.pdf
│   │   └── password_change_lifecycle.md
│   │
│   ├── api_calls.md
│   ├── api_responses.md
│   ├── authentication.md
│   ├── cryptographic_implementation.md
│   └── database_schema.md
│
├── src
│
└── tests
```
