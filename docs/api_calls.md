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
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| srp_salt        | string | Yes      | **Base64-encoded** salt generated for SRP        |
| srp_verifier    | string | Yes      | **Base64-encoded** verifier derived for SRP      |
| master_key_salt | string | Yes      | **Base64-encoded** salt generated for master key |

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/user/register \
    -H "Content-Type: application/json" \
    -d '{
        "username": "123hashedUsername",
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
        "session_id": "abc123sessionId",
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
| username        | string | Yes      | Hash of the user's username.                     |

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
        "session_id": "abc123sessionId",
        "request_number": 0,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Health Check
**Endpoint**
`GET /api/user/health`

**Description**
Check the health and availability of the User API endpoints. Returns system status information.

**Parameters**
None required.

**Example Request**
```bash
curl -X GET https://[API_BASE_URL]/api/user/health \
    -H "Content-Type: application/json"
```

---


## Password

Handles the complex multi-step password change process with special security sessions.

### Start Password Change
**Endpoint**
`POST /api/password/start`

**Description**
Begins the process of a password change, returning the user's validation details to create a password session.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session.              |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                           |
|-----------------|--------|----------|-------------------------------------------------------|
| username        | string | Yes      | Hash of the original username.                        |
| srp_salt        | string | Yes      | **Base64-encoded** salt generated for new SRP.        |
| srp_verifier    | string | Yes      | **Base64-encoded** verifier derived for new SRP.      |
| master_key_salt | string | Yes      | **Base64-encoded** salt generated for new master key. |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: srp_salt length][srp_salt bytes]
[4 bytes: srp_verifier length][srp_verifier bytes]
[4 bytes: master_key_salt length][master_key_salt bytes]
```

> **Note:** An existing auth session is required in order to start a password change auth session.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/start \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Continue Password Change
**Endpoint**
`POST /api/password/auth`

**Description**
Completes the SRP authentication process by providing client ephemeral value and proof. Returns session details and server proof for verification. Also returns list of all data entry public IDs.

**Parameters**
| Field            | Type   | Required | Description                                          |
|------------------|--------|----------|------------------------------------------------------|
| session_id       | string | Yes      | The public ID of the login session.                  |
| request_number   | int    | Yes      | The number of this request on the login session.     |
| encrypted_data   | string | Yes      | **Base64-encoded** encrypted payload (see below)     |

**Encryption Payload**
| Field           | Type   | Required | Description                                           |
|-----------------|--------|----------|-------------------------------------------------------|
| username        | string | Yes      | Hash of the original username.                        |
| auth_id         | string | Yes      | Public ID of the AuthEphemeral being used.            |
| eph_val_a       | string | Yes      | **Base64-encoded** client ephemeral value. (A)        |
| proof_val_m1    | string | Yes      | **Base64-encoded** client proof. (M1)                 |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: auth_id length][auth_id bytes]
[4 bytes: eph_val_a length][eph_val_a bytes]
[4 bytes: proof_val_m1 length][proof_val_m1 bytes]
```

> **Note:** Password changing sessions expire after 5 minutes.
> **Note:** Password changing sessions have a limited number of requests based on the user's number of password entries. (Enough requests to read and write to each password once, with an additional request to complete the password change.)
> **Note:** A user can only have one active password changing session.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/auth \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Complete Password Change
**Endpoint**
`POST /api/password/complete`

**Description**
Complete a password change. If all entries have been completed, the change is confirmed, and the old password details are erased.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/complete \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Abort Password Change
**Endpoint**
`POST /api/password/abort`

**Description**
Abort a password change that is in progress. Deletes all details about the new password.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session.              |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/abort \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Request Entry
**Endpoint**
`POST /api/password/request`

**Description**
Request the encrypted name and data for a given data entry, as well as its unique encryption data.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| entry_public_id | string | Yes      | Public ID of the entry being requested.          |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/request \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Add New Encryption for Entry
**Endpoint**
`POST /api/password/update`

**Description**
Set the encrypted name and data for a given data entry, encrypted with the new master key. Also provide the new unique encryption data.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the login session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| entry_public_id | string | Yes      | Public ID of the entry being updated.            |
| entry_name      | string | Yes      | The new encrypted entry name payload.            |
| entry_data      | string | Yes      | The new encrypted entry data payload.            |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
[4 bytes: entry_name length][entry_name bytes]
[4 bytes: entry_data length][entry_data bytes]
```

> **⚠️ CRITICAL:** The newly encrypted entry name and data must be encrypted using the new master key.
> **⚠️ CRITICAL:** A new nonce must be generated for each encryption. The old nonce must not be reused.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/request \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Health Check
**Endpoint**
`GET /api/password/health`

**Description**
Check the health and availability of the Password API endpoints. Returns system status information.

**Parameters**
None required.

**Example Request**
```bash
curl -X GET https://[API_BASE_URL]/api/password/health \
    -H "Content-Type: application/json"
```

---


## Session

Manages authentication sessions using SRP protocol for secure login and logout.

### Start Auth
**Endpoint**
`POST /api/session/start`

**Description**
Request the details to create a new login session, including SRP details, master key salt, and server ephemeral value for SRP authentication.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/start \
    -H "Content-Type: application/json" \
    -d '{
        "username": "123hashedUsername"
    }'
```


### Complete Auth
**Endpoint**
`POST /api/session/auth`

**Description**
Completes the SRP authentication process by providing client ephemeral value and proof. Returns session details and server proof for verification.

**Parameters**
| Field            | Type   | Required | Description                                          |
|------------------|--------|----------|------------------------------------------------------|
| username         | string | Yes      | Hash of the user's username.                         |
| auth_id          | string | Yes      | Public ID of the AuthEphemeral being used.           |
| eph_val_a        | string | Yes      | **Base64-encoded** client ephemeral value. (A)       |
| proof_val_m1     | string | Yes      | **Base64-encoded** client proof. (M1)                |
| maximum_requests | int    | No       | Number of requests before the session will expire.   |
| expiry_time      | int    | No       | Session expiry time in seconds from now.             |

> **Note:** If left blank, maximum requests will default to 100, and expiry time will default to 3600.
> **Note:** Maximum requests can be set to unlimited using a value of -1.
> **Note:** Expiry time can be set to unlimited using a value of -1.
> **⚠️ CRITICAL:** Sessions with unlimited requests and time will never naturally expire, and must be manually purged using the [Delete Session](#delete-session) or [Clean Sessions](#clean-sessions) APIs.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/auth \
    -H "Content-Type: application/json" \
    -d '{
        "username": "123hashedUsername",
        "eph_val_a": "base64ClientEphemeral",
        "proof_val_m1": "base64ClientProof",
        "maximum_requests": 50,
        "expiry_time": 1800
    }'
```


### Delete Session
**Endpoint**
`POST /api/session/delete`

**Description**
Delete the given auth session from the database, preventing further use.

**Parameters**
| Field           | Type   | Required | Description                                                         |
|-----------------|--------|----------|---------------------------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session being used to auth this request. |
| request_number  | int    | Yes      | The number of this request on the login session.                    |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below)                    |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| session_id      | string | Yes      | Public ID of the session to be deleted.          |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: session_id length][session_id bytes]
```

> **Note:** The session being deleted does not need to be the one in use.
> **Note:** Deleting a password change session this way will terminate the password change.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/delete \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Clean Sessions
**Endpoint**
`POST /api/session/clean`

**Description**
Delete all existing auth sessions from the database, preventing further use.

**Parameters**
| Field           | Type   | Required | Description                                                         |
|-----------------|--------|----------|---------------------------------------------------------------------|
| session_id      | string | Yes      | The public ID of the login session being used to auth this request. |
| request_number  | int    | Yes      | The number of this request on the login session.                    |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below)                    |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

> **Note:** The session being used to auth this request will also be deleted.
> **Note:** Deleting a password change session this way will terminate the password change.

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/clean \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```


### Health Check
**Endpoint**
`GET /api/session/health`

**Description**
Check the health and availability of the Session API endpoints. Returns system status information.

**Parameters**
None required.

**Example Request**
```bash
curl -X GET https://[API_BASE_URL]/api/session/health \
    -H "Content-Type: application/json"
```

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
**Endpoint**
`GET /api/data/health`

**Description**
Check the health and availability of the Data API endpoints. Returns system status information.

**Parameters**
None required.

**Example Request**
```bash
curl -X GET https://[API_BASE_URL]/api/data/health \
    -H "Content-Type: application/json"
```
