# API Responses

A brief introduction to the possible responses for all defined APIs.
([See API Requests](api_calls.md))

## Overview
1. [**User**](#user)
    1. [Register User](#register-user-post)
    2. [Change Username](#change-username)
    3. [Delete User](#delete-user)
    4. [Health Check](#health-check)
2. [**Password**](#password)
    1. [Start Password Change](#start-password-change)
    2. [Continue Password Change](#continue-password-change)
    3. [Complete Password Change](#complete-password-change)
    4. [Abort Password Change](#abort-password-change)
    5. [Request Entry](#request-entry)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry)
3. [**Session**](#session)
    1. [Start Auth](#start-auth)
    2. [Complete Auth](#complete-auth)
    3. [Delete Session](#delete-session)
    4. [Clean Sessions](#clean-sessions)
    5. [Health Check](#health-check-1)
4. [**Data**](#data)
    1. [Create Entry](#create-entry)
    2. [Edit Entry](#edit-entry)
    3. [Delete Entry](#delete-entry)
    4. [Retrieve Entry](#retrieve-entry)
    5. [Retrieve List](#retrieve-list)
    6. [Health Check](#health-check-2)
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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
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

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: session_id length][session_id bytes]
[4 bytes: server_proof_m2 length][server_proof_m2 bytes]
```

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
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
| DECRYPTION_ERROR    | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND           | 404         | The requested item could not be found.                         |
| PRECONDITION_FAILED | 412         | The preconditions have not been met to complete this function. |
| INTERNAL_ERROR      | 500         | Server encountered an unexpected error.                        |


### Abort Password Change
TODO

### Request Entry
TODO

### Add New Encryption for Entry
TODO

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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| NOT_FOUND        | 404         | The requested item could not be found.                         |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |

---


## Data

### Create Entry
TODO

### Edit Entry
TODO

### Delete Entry
TODO

### Retrieve Entry
TODO

### Retrieve List
TODO

---

## Other Responses

### Error Messages
TODO

### HTTP Status Codes
TODO
