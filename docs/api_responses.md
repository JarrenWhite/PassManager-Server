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

**Success Response**
201

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
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| new_username    | bytes  | Yes      | Hash of the new username.                        |

**Encryption Encoding**
```
[4 bytes: new_username length][new_username bytes]
```

**Success Response**
200

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
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username_hash   | bytes  | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| auth_id         | string   | success  | The public ID of the in progress auth request.               |
| srp_salt        | bytes    | success  | The salt used to create the verifier in SRP.                 |
| eph_public_b    | bytes    | success  | Unique server ephemeral value (B) for this SRP auth attempt. |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: auth_id length][auth_id bytes]
[4 bytes: srp_salt length][srp_salt bytes]
[4 bytes: eph_public_b length][eph_public_b bytes]
```

**Success Response**
201

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| session_id      | string   | success  | The public ID of the created password session.               |
| server_proof_m2 | bytes    | success  | The server's proof of authentication.                        |
| entry_ids       | [string] | success  | The public IDs of all stored data entries.                   |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: session_id length][session_id bytes]
[4 bytes: server_proof_m2 length][server_proof_m2 bytes]
[4 bytes: entry_ids length][entry_ids bytes]
```

**Success Response**
201

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |
| entry_name      | bytes    | Yes      | Encrypted entry name payload.                                |
| entry_data      | bytes    | Yes      | Encrypted entry data payload.                                |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
[4 bytes: entry_name length][entry_name bytes]
[4 bytes: entry_data length][entry_data bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**Success Response**
200

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

**Success Response**
201

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

**Success Response**
201

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
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username_hash   | bytes  | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

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
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username_hash   | bytes  | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**Success Response**
201

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |
| entry_name      | bytes    | Yes      | Encrypted entry name payload.                                |
| entry_data      | bytes    | Yes      | Encrypted entry data payload.                                |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
[4 bytes: entry_name length][entry_name bytes]
[4 bytes: entry_data length][entry_data bytes]
```

**Success Response**
200

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
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Yes      | Hash of the user's username.                                 |
| entry_ids       | [bytes]  | success  | The public IDs of all stored data entries.                   |
| entry_names     | [bytes]  | success  | The name payload for all stored data entries.                |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
[4 bytes: entry_ids length][entry_ids bytes]
[4 bytes: entry_names length][entry_names bytes]
```

**Success Response**
200

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

| Error Code | Field           | HTTP Code | Error Message                                                |
|------------|-----------------|-----------|--------------------------------------------------------------|
| rqs00      | request         | 400       | Incorrect parameters. Required: [\<fields\>]                 |
| rqs01      | request         | 401       | Failed to decrypt payload, invalid session or corrupted data |
| rqs02      | request         | 403       | Password change in progress                                  |
| rqs03      | request         | 429       | Too many requests                                            |
| svr00      | server          | 500       | Server encountered an unexpected error                       |
| svr01      | server          | 503       | Temporary outage/maintenance                                 |


### General Field Errors

These can be returned in response to multiple possible fields.

| Error Code | HTTP Code | Error message       |
|------------|-----------|---------------------|
| gnr00      | 400       | \<Field\> invalid   |
| gnr01      | 404       | \<Field\> not found |


### Limited API Errors

These errors are specific to certain APIs. Only those APIs can return these errors.

| Error Code | Field           | HTTP Code | APIs | Error Message                                                |
|------------|-----------------|-----------|------|--------------------------------------------------------------|
| ltd00      | username_hash   | 409       | [Register User](#register-user-user) [Change Username](#change-username-user) | New username already exists |
| ltd01      | request_number  | 400       | [Delete User](#delete-user-user) | Request number must be 0 for this request type                   |
| ltd02      | request         | 412       | [Complete Password Change](#complete-password-change-password) | Password change is not complete                     |


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
