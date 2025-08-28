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
- `{type}` can be: `user`, `session`, `data`
- `{callName}` is the specific endpoint name

---


## User

### Register User [POST]
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
