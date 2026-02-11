# API Responses

A brief introduction to the possible responses for all defined APIs.
([See API Requests](api_calls.md))

## Overview
1. [**User**](#user)
    1. [Register User](#register-user-user)
    2. [Change Username](#change-username-user)
    3. [Delete User](#delete-user-user)
2. [**Password**](#password)
    1. [Start Password Change](#start-password-change-password)
    2. [Continue Password Change](#continue-password-change-password)
    3. [Complete Password Change](#complete-password-change-password)
    4. [Abort Password Change](#abort-password-change-password)
    5. [Get Entry](#get-entry-password)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry-password)
3. [**Session**](#session)
    1. [Start Auth](#start-auth-session)
    2. [Complete Auth](#complete-auth-session)
    3. [Delete Session](#delete-session-session)
    4. [Clean Sessions](#clean-sessions-session)
4. [**Data**](#data)
    1. [Create Entry](#create-entry-data)
    2. [Edit Entry](#edit-entry-data)
    3. [Delete Entry](#delete-entry-data)
    4. [Get Entry](#get-entry-data)
    5. [Get List](#get-list-data)
5. [**Errors**](#errors)
    1. [Error Messages](#error-messages)
    2. [Request Errors](#request-errors)
    3. [General Field Errors](#general-field-errors)
    4. [Limited API Errors](#limited-api-errors)
    5. [HTTP Status Codes](#http-status-codes)

---


## User

### Register User (User)

**[Request Format](api_calls.md#register-user-user)**

**Response Fields**
| Field           | Type     | When     | Description                                |
|-----------------|----------|----------|--------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful. |
| username_hash   | bytes    | success  | Hash of the username that was registered.  |
| errors          | [error]  | failure  | json list of each error.                   |

---

### Change Username (User)

**[Request Format](api_calls.md#change-username-user)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| new_username    | bytes  | Hash of the new username.                        |

---

### Delete User (User)

**[Request Format](api_calls.md#delete-user-user)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---


## Password

### Start Password Change (Password)

**[Request Format](api_calls.md#start-password-change-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| auth_id         | string   | The public ID of the in progress auth request.               |
| srp_salt        | bytes    | The salt used to create the verifier in SRP.                 |
| eph_public_b    | bytes    | Unique server ephemeral value (B) for this SRP auth attempt. |

---

### Continue Password Change (Password)

**[Request Format](api_calls.md#continue-password-change-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| session_id      | string   | The public ID of the created password session.               |
| server_proof_m2 | bytes    | The server's proof of authentication.                        |
| entry_ids       | [string] | The public IDs of all stored data entries.                   |

---

### Complete Password Change (Password)

**[Request Format](api_calls.md#complete-password-change-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the password change session.    |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |

---

### Abort Password Change (Password)

**[Request Format](api_calls.md#abort-password-change-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |

---

### Get Entry (Password)

**[Request Format](api_calls.md#get-entry-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the password change session.    |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |
| entry_name      | bytes    | Encrypted entry name payload.                                |
| entry_data      | bytes    | Encrypted entry data payload.                                |

---

### Add New Encryption for Entry (Password)

**[Request Format](api_calls.md#add-new-encryption-for-entry-password)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the password change session.    |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---


## Session

### Start Auth (Session)

**[Request Format](api_calls.md#start-auth-session)**

**Response Fields**
| Field           | Type     | When     | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.                   |
| auth_id         | string   | success  | The public ID of the in progress auth request.               |
| srp_salt        | bytes    | success  | The salt used to create the verifier in SRP.                 |
| eph_public_b    | bytes    | success  | Unique server ephemeral value (B) for this SRP auth attempt. |
| master_key_salt | bytes    | success  | The salt used to create the master key.                      |
| errors          | [error]  | failure  | json list of each error.                                     |

---

### Complete Auth (Session)

**[Request Format](api_calls.md#complete-auth-session)**

**Response Fields**
| Field           | Type     | When     | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.                   |
| session_id      | string   | success  | The public ID of the created session.                        |
| server_proof_m2 | bytes    | success  | The server's proof of authentication.                        |
| errors          | [error]  | failure  | json list of each error.                                     |

---

### Delete Session (Session)

**[Request Format](api_calls.md#delete-session-session)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---

### Clean Sessions (Session)

**[Request Format](api_calls.md#clean-sessions-session)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---


## Data

### Create Entry (Data)

**[Request Format](api_calls.md#create-entry-data)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Edit Entry (Data)

**[Request Format](api_calls.md#edit-entry-data)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Delete Entry (Data)

**[Request Format](api_calls.md#delete-entry-data)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Get Entry (Data)

**[Request Format](api_calls.md#get-entry-data)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |
| entry_name      | bytes    | Encrypted entry name payload.                                |
| entry_data      | bytes    | Encrypted entry data payload.                                |

---

### Get List (Data)

**[Request Format](api_calls.md#get-list-data)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | success  | The public ID of the login session.              |
| encrypted_data  | bytes    | success  | Encrypted payload. (see below)                   |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_ids       | [bytes]  | The public IDs of all stored data entries.                   |
| entry_names     | [bytes]  | The name payload for all stored data entries.                |

---


## Errors

### Error Messages

Error messages are returned in the format:
{"field": field_name, "error_code": error_code, "error": error_message}

- The `error_code` is stable and intended for programmatic handling.
- The `error` message is human-readable and is subject to change. It should be used for logging and debugging only.

Example failure response:
```json
{
  "success": false,
  "errors": [
    { "field": "request", "error_code": "rqs00", "error": "Incorrect parameters. Required: [new_username, srp_salt, srp_verifier, master_key_salt]" }
  ]
}
```

Notes:
- Multiple errors may be returned in a single response. Clients should iterate the `errors` array.
- Error code naming scheme:
  - `rqsXX`: request-level errors that apply to the entire request.
  - `svrXX`: server-level errors that apply to the application.
  - `gnrXX`: general field errors that can apply to multiple APIs/fields.
  - `ltdXX`: limited API errors that apply to specific endpoints only.


### Request Errors

These errors can be returned to any possible request.

| Error Code | Field           | Error Message                                                |
|------------|-----------------|--------------------------------------------------------------|
| RQS00      | request         | Incorrect parameters. Required: [\<fields\>]                 |
| RQS01      | request         | Failed to decrypt payload, invalid session or corrupted data |
| RQS02      | request         | Password change in progress                                  |
| RQS03      | request         | Too many requests                                            |
| SVR00      | server          | Server encountered an unexpected error                       |
| SVR01      | server          | Temporary outage/maintenance                                 |


### General Field Errors

These can be returned in response to multiple possible fields.

| Error Code | Error message       |
|------------|---------------------|
| GNR00      | \<Field\> invalid   |
| GNR01      | \<Field\> not found |


### Operation Specific Errors

These errors are specific to certain APIs. Only those APIs can return these errors.

| Error Code | Field           | APIs | Error Message                                                |
|------------|-----------------|------|--------------------------------------------------------------|
| OPR00      | username_hash   | [Register User](#register-user-user) [Change Username](#change-username-user) | New username already exists |
| OPR01      | request_number  | [Delete User](#delete-user-user) | Request number must be 0 for this request type                   |
| OPR02      | request         | [Complete Password Change](#complete-password-change-password) | Password change is not complete                     |


### HTTP Status Codes

A HTTP response code is issued with every response. Where multiple possible response codes are true at once, the highest importance code will be returned.

| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| SUCCESS             | 201         | Resource created.                                              |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| FORBIDDEN           | 403         | User is undergoing a password change.                          |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| USER_EXISTS         | 409         | Username hash already exists.                                  |
| PRECONDITION_FAILED | 412         | The preconditions have not been met to complete this function. |
| RATE_LIMIT_EXCEEDED | 429         | Too many requests.                                             |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |
| SERVICE_UNAVAILABLE | 503         | Temporary outage or maintenance.                               |
