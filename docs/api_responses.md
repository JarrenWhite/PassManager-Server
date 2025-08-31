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
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| FORBIDDEN        | 403         | User is undergoing a password change.                          |
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
| new_username    | string | Yes      | Hash of the username.                            |

**Encryption Encoding**
```
[4 bytes: new_username length][new_username bytes]
```

**Common Response Codes**
| Response Code    | HTTP Status | Description                                                    |
|------------------|-------------|----------------------------------------------------------------|
| SUCCESS          | 200         | OK.                                                            |
| DECRYPTION_ERROR | 401         | Failed to decrypt payload - invalid session or corrupted data. |
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing.                     |
| FORBIDDEN        | 403         | User is undergoing a password change.                          |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error.                        |


### Health Check
TODO

---


## Password

### Start Password Change
TODO

### Continue Password Change
TODO

### Complete Password Change
TODO

### Abort Password Change
TODO

### Request Entry
TODO

### Add New Encryption for Entry
TODO

### Health Check
TODO

---


## Session

### Start Auth
TODO

### Complete Auth
TODO

### Delete Session
TODO

### Clean Sessions
TODO

### Health Check
TODO

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

### Health Check
TODO

---

## Other Responses

### Error Messages
TODO

### HTTP Status Codes
TODO
