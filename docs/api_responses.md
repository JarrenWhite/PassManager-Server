# API Responses

A brief introduction to the possible responses for all defined APIs.
([See API Requests](api_calls.md))

## Overview
1. [**User**](#user)
    1. [Register User](#register-user-post)
    2. [Change Username](#change-username)
    3. [Delete User](#delete-user)
2. [**Password**](#password)
    1. [Start Password Change](#start-password-change)
    2. [Continue Password Change](#continue-password-change)
    3. [Complete Password Change](#complete-password-change)
    4. [Abort Password Change](#abort-password-change)
    5. [Get Entry](#get-entry)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry)
3. [**Session**](#session)
    1. [Start Auth](#start-auth)
    2. [Complete Auth](#complete-auth)
    3. [Delete Session](#delete-session)
    4. [Clean Sessions](#clean-sessions)
4. [**Data**](#data)
    1. [Create Entry](#create-entry)
    2. [Edit Entry](#edit-entry)
    3. [Delete Entry](#delete-entry)
    4. [Get Entry](#get-entry-1)
    5. [Get List](#get-list)
5. [**Errors**](#errors)
    1. [Error Messages](#error-messages)
    2. [Request Errors](#request-errors)
    3. [General Field Errors](#general-field-errors)
    4. [Limited API Errors](#limited-api-errors)
    5. [HTTP Status Codes](#http-status-codes)

---


## User

### Register User (User)

**[Request Format](api_calls.md#register-user)**

**Response Fields**
| Field           | Type     | When     | Description                                |
|-----------------|----------|----------|--------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful. |
| username_hash   | string   | success  | Hash of the username that was registered.  |
| username_id     | string   | success  | Public ID for the new user account         |
| errors          | [error]  | failure  | json list of each error.                   |

**Success Response**
201

---

### Change Username (User)

**[Request Format](api_calls.md#change-username)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| new_username    | string | Yes      | Hash of the new username.                        |

**Encryption Encoding**
```
[4 bytes: new_username length][new_username bytes]
```

**Success Response**
200

---

### Delete User (User)

**[Request Format](api_calls.md#delete-user)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

---


## Password

### Start Password Change (Password)

**[Request Format](api_calls.md#start-password-change)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
| auth_id         | string   | success  | The public ID of the in progress auth request.               |
| srp_salt        | string   | success  | The salt used to create the verifier in SRP.                 |
| ephemeral_b     | string   | success  | Unique server ephemeral value (B) for this SRP auth attempt. |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: auth_id length][auth_id bytes]
[4 bytes: srp_salt length][srp_salt bytes]
[4 bytes: ephemeral_b length][ephemeral_b bytes]
```

**Success Response**
201

---

### Continue Password Change (Password)

**[Request Format](api_calls.md#continue-password-change)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
| session_id      | string   | success  | The public ID of the created password session.               |
| server_proof_m2 | string   | success  | The server's proof of authentication.                        |
| entry_ids       | [string] | success  | The public IDs of all stored data entries.                   |
| entry_names     | [string] | success  | The name payload for all stored data entries.                |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: session_id length][session_id bytes]
[4 bytes: server_proof_m2 length][server_proof_m2 bytes]
[4 bytes: entry_ids length][entry_ids bytes]
[4 bytes: entry_names length][entry_names bytes]
```

**Success Response**
201

---

### Complete Password Change (Password)

**[Request Format](api_calls.md#complete-password-change)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the password change session.    |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

---

### Abort Password Change (Password)

**[Request Format](api_calls.md#abort-password-change)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

---

### Get Entry (Password)

**[Request Format](api_calls.md#get-entry)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the password change session.    |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |
| entry_name      | string   | Yes      | The new encrypted entry name payload.                        |
| entry_data      | string   | Yes      | The new encrypted entry data payload.                        |

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

**[Request Format](api_calls.md#add-new-encryption-for-entry)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the password change session.    |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
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

**[Request Format](api_calls.md#start-auth)**

**Response Fields**
| Field           | Type     | When     | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.                   |
| auth_id         | string   | success  | The public ID of the in progress auth request.               |
| srp_salt        | string   | success  | The salt used to create the verifier in SRP.                 |
| ephemeral_b     | string   | success  | Unique server ephemeral value (B) for this SRP auth attempt. |
| master_key_salt | string   | success  | The salt used to create the master key.                      |
| errors          | [error]  | failure  | json list of each error.                                     |

**Success Response**
201

---

### Complete Auth (Session)

**[Request Format](api_calls.md#complete-auth)**

**Response Fields**
| Field           | Type     | When     | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.                   |
| session_id      | string   | success  | The public ID of the created session.                        |
| server_proof_m2 | string   | success  | The server's proof of authentication.                        |
| errors          | [error]  | failure  | json list of each error.                                     |

**Success Response**
201

---

### Delete Session (Session)

**[Request Format](api_calls.md#delete-session)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

---

### Clean Sessions (Session)

**[Request Format](api_calls.md#clean-sessions)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Success Response**
200

---


## Data

### Create Entry (Data)

**[Request Format](api_calls.md#create-entry)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
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

**[Request Format](api_calls.md#edit-entry)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
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

**[Request Format](api_calls.md#delete-entry)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
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

**[Request Format](api_calls.md#get-entry-1)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |
| entry_name      | string   | Yes      | The new encrypted entry name payload.                        |
| entry_data      | string   | Yes      | The new encrypted entry data payload.                        |

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

**[Request Format](api_calls.md#get-list)**

**Response Fields**
| Field           | Type     | When     | Description                                      |
|-----------------|----------|----------|--------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.       |
| session_id      | string   | always   | The public ID of the login session.              |
| encrypted_data  | string   | success  | **Base64-encoded** encrypted payload (see below) |
| errors          | [error]  | failure  | json list of each error.                         |

**Encryption Payload**
| Field           | Type     | Required | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| username        | string   | Yes      | Hash of the user's username.                                 |
| entry_public_id | string   | Yes      | Public ID of the entry.                                      |
| entry_ids       | [string] | success  | The public IDs of all stored data entries.                   |
| entry_names     | [string] | success  | The name payload for all stored data entries.                |

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


### Request Errors

These errors can be returned to any possible request.

| Error Code | Field           | HTTP Code | Error Message                                                |
|------------|-----------------|-----------|--------------------------------------------------------------|
| rqs00      | request         | 400       | Incorrect parameters. Required: []                           |
| rqs01      | request         | 401       | Failed to decrypt payload, invalid session or corrupted data |
| rqs02      | request         | 403       | Password change in progress                                  |
| svr00      | server          | 500       | Server encountered an unexpected error                       |


### General Field Errors

These can be returned in response to multiple possible fields.

| Error Code | HTTP Code | Error message     |
| gnr00      | 401       | {Field} invalid   |
| gnr01      | 404       | {Field} not found |


### Limited API Errors

These errors are specific to certain APIs. Only those APIs can return these errors.

| Error Code | Field           | HTTP Code | APIs | Error Message                                                |
|------------|-----------------|-----------|-----|--------------------------------------------------------------|
| ltd00      | new_username    | 409       | [Register User](#register-user-user) [Change Username](#change-username-user) | New username already exists |
| ltd01      | request_number  | 400       | [Change Username](#change-username-user) | Request number must be 0 for this request type                   |
| ltd02      | request         | 412       | [Complete Password Change](#complete-password-change) | Password change is not complete                     |


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
| USER_EXISTS         | 409         | Username hash already exists in the system.                    |
| PRECONDITION_FAILED | 412         | The preconditions have not been met to complete this function. |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |
