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
5. [**Other Responses**](#other-responses)
    1. [Error Messages](#error-messages)
    2. [HTTP Status Codes](#http-status-codes)

---


## User

### Register User

**[Request Format](api_calls.md#register-user)**

**Response Fields**
| Field           | Type     | When     | Description                                |
|-----------------|----------|----------|--------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful. |
| username_hash   | string   | always   | Hash of the username that was registered.  |
| username_id     | string   | success  | Public ID for the new user account         |
| errors          | [error]  | failure  | json list of each error.                   |

**Common Response Codes**
| Response Code    | HTTP Status | Description                                      |
|------------------|-------------|--------------------------------------------------|
| SUCCESS          | 201         | Resource created.                                |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.       |
| USER_EXISTS      | 409         | Username hash already exists in the system.      |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.          |


### Change Username

**[Request Format](api_calls.md#register-user)**

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| FORBIDDEN        | 403         | User is undergoing a password change.                          |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Delete User

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| FORBIDDEN        | 403         | User is undergoing a password change.                          |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |

---


## Password

### Start Password Change

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Continue Password Change

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Complete Password Change

**[Request Format](api_calls.md#complete-password-change)**

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| PRECONDITION_FAILED | 412         | The preconditions have not been met to complete this function. |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Abort Password Change

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Get Entry

**[Request Format](api_calls.md#get-entry)**

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Add New Encryption for Entry

**[Request Format](api_calls.md#add-new-encryption-for-entry)**

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |

---


## Session

### Start Auth

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Complete Auth

**[Request Format](api_calls.md#complete-auth)**

**Response Fields**
| Field           | Type     | When     | Description                                                  |
|-----------------|----------|----------|--------------------------------------------------------------|
| success         | boolean  | always   | Indicates if the operation was successful.                   |
| session_id      | string   | success  | The public ID of the created session.                        |
| server_proof_m2 | string   | success  | The server's proof of authentication.                        |
| errors          | [error]  | failure  | json list of each error.                                     |

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Delete Session

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Clean Sessions

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

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED     | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |

---


## Data

### Create Entry

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| LOCKED              | 423         | Cannot execute at this time.                                   |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Edit Entry

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| LOCKED              | 423         | Cannot execute at this time.                                   |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Delete Entry

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| LOCKED              | 423         | Cannot execute at this time.                                   |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Get Entry

**[Request Format](api_calls.md#get-entry)**

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| LOCKED              | 423         | Cannot execute at this time.                                   |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Get List

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

**Common Response Codes**
| Response Code       | HTTP Status | Description                                                    |
|---------------------|-------------|----------------------------------------------------------------|
| SUCCESS             | 200         | OK.                                                            |
| VALIDATION_ERROR    | 400         | Request parameters are invalid or missing.                     |
| UNAUTHORISED        | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| LOCKED              | 423         | Cannot execute at this time.                                   |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |

---


## Other Responses

### Error Messages
TODO

### HTTP Status Codes
TODO
