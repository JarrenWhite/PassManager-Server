

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

**📋 [Request Format](api_calls.md#register-user)**

**Response Fields**
| Field           | When     | Type     | Description                                |
|-----------------|----------|----------|--------------------------------------------|
| success         | always   | boolean  | Indicates if the operation was successful. |
| username_hash   | always   | string   | Hash of the username that was registered.  |
| username_id     | success  | string   | Public ID for the new user account         |
| errors          | failure  | [string] | json list of each error.                   |

**Success Response (201 Created)**
```json
{
    "success": true,
    "username_hash": "123hashedUsername",
    "username_id": "idForUsername123"
}
```

**Error Response (400 Bad Request)**
```json
{
    "success": false,
    "username_hash": "123hashedUsername",
    "errors": [
        {"field": "session_id", "message": "Field is not known"},
        {"field": "srp_verifier", "message": "srp_verifier is too short"}
    ]
}
```

**Error Response (409 Conflict)**
```json
{
    "success": false,
    "username_hash": "123hashedUsername",
    "errors": [
        {"field": "username", "message": "Username already exists"},
    ]
}
```

**Error Response (500 Internal Server Error)**
```json
{
    "success": false,
    "username_hash": "123hashedUsername",
    "errors": [
        {"field": "other", "message": "Unknown server error"},
    ]
}
```

**Common Error Codes**
| Error Code       | HTTP Status | Description                                      |
|------------------|-------------|--------------------------------------------------|
| VALIDATION_ERROR | 400         | Request parameters are invalid or missing        |
| USER_EXISTS      | 409         | Username hash already exists in the system      |
| INTERNAL_ERROR   | 500         | Server encountered an unexpected error          |


### Change Username
TODO

### Delete User
TODO

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
