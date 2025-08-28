# API Calls

A brief introduction to the API, its purpose, and how to make API calls.

> **API Base URL:** `https://[API_BASE_URL]`
> **TODO:** *Replace `[API_BASE_URL]` with the actual domain when determined*

## Overview
1. [**Base URL**](#base-url)
2. [**API Structure**](#api-structure)
3. [**User**](#user)
    1. [Register User](#register-user-post)
    2. [Change Username](#change-username)
    3. [Change Password](#change-password-future)
    4. [Delete User](#delete-user)
    5. [Health Check](#health-check)
4. [**Password**](#password)
    1. [Start Password Change](#start-password-change)
    2. [Continue Password Change](#continue-password-change)
    3. [Complete Password Change](#complete-password-change)
    4. [Abort Password Change](#abort-password-change)
    5. [Request Entry](#request-entry)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry)
5. [**Session**](#session)
    1. [Start Auth](#start-auth)
    2. [Complete Auth](#complete-auth)
    3. [Delete Session](#delete-session)
    4. [Clean Sessions](#clean-sessions)
    5. [Health Check](#health-check-1)
6. [**Data**](#data)
    1. [Create Entry](#create-entry)
    2. [Edit Entry](#edit-entry)
    3. [Delete Entry](#delete-entry)
    4. [Retrieve Entry](#retrieve-entry)
    5. [Retrieve List](#retrieve-list)
    6. [Health Check](#health-check-2)

---


## Base URL
```https://[API_BASE_URL]```

---


## API Structure
API endpoints follow the pattern: `/api/{type}/{callName}`

Where:
- `{type}` can be: `user`, `password`, `session`, `data`
- `{callName}` is the specific endpoint name

---


## User

Manages user account operations including registration, username changes, and account deletion.

### Register User
**Endpoint**
`POST /api/user/register`

**Description**
Creates a new user account using a username hash, and the required security information.

**Parameters**
| Field           | Type   | Required | Description                                    |
|-----------------|--------|----------|------------------------------------------------|
| username        | string | Yes      | Hash of the username.                          |
| srp_salt        | string | Yes      | **Base64-encoded** salt (stored as binary)     |
| srp_verifier    | string | Yes      | **Base64-encoded** verifier (stored as binary) |
| master_key_salt | string | Yes      | **Base64-encoded** salt (stored as binary)     |

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/user/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "",
        "srp_salt": "base64Salt",
        "srp_verifier": "base64Verifier",
        "master_key_salt": "base64MasterSalt"
    }'
```


### Change Username
**Endpoint**
`POST /api/user/username`

**Description**
Changes a user's username, from one username hash, to another username hash.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session.              |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the original username.                   |
| new_username    | string | Yes      | Hash of the new username.                        |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: new_username length][new_username bytes]
```

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/user/username \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionid",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Delete User
**Endpoint**
`POST /api/user/delete`

**Description**
Delete a given user, and all data associated with their account.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session.              |
| request_number  | int    | Yes      | The number of this request on the login session. Must be 0 for this request type. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the username to be deleted.              |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

> **Note:** The request number for this request type must be 0. This means a new session must be created for user deletion.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/user/delete \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionid",
        "request_number": 0,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Health Check
TODO

---


## Password

Handles the complex multi-step password change process with special security sessions.

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

---


## Session

Manages authentication sessions using SRP protocol for secure login and logout.

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

Handles encrypted password entry operations including create, read, update, and delete.

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
