# API Calls

A brief introduction to the API, its purpose, and how to make API calls.
([See API Responses](api_responses.md))

> **API Base URL:** `https://[API_BASE_URL]`
> **TODO:** *Replace `[API_BASE_URL]` with the actual domain when determined*

## Overview
1. [**Base URL**](#base-url)
2. [**API Structure**](#api-structure)
3. [**User**](#user)
    1. [Register User](#register-user-user)
    2. [Change Username](#change-username-user)
    3. [Delete User](#delete-user-user)
    4. [Health Check](#health-check-user)
4. [**Password**](#password)
    1. [Start Password Change](#start-password-change-password)
    2. [Continue Password Change](#continue-password-change-password)
    3. [Complete Password Change](#complete-password-change-password)
    4. [Abort Password Change](#abort-password-change-password)
    5. [Get Entry](#get-entry-password)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry-password)
    7. [Health Check](#health-check-password)
5. [**Session**](#session)
    1. [Start Auth](#start-auth-session)
    2. [Complete Auth](#complete-auth-session)
    3. [Delete Session](#delete-session-session)
    4. [Clean Sessions](#clean-sessions-session)
    5. [Health Check](#health-check-session)
6. [**Data**](#data)
    1. [Create Entry](#create-entry-data)
    2. [Edit Entry](#edit-entry-data)
    3. [Delete Entry](#delete-entry-data)
    4. [Get Entry](#get-entry-data)
    5. [Get List](#get-list-data)
    6. [Health Check](#health-check-data)

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

> **Note:** User operations use regular "Login Sessions" for authentication, except for user registration which requires no authentication.

### Register User (User)
**Endpoint**
`POST /api/user/register`

**Description**
Creates a new user account using a username hash, and the required security information.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| new_username    | string | Yes      | Hash of the new username.                        |
| srp_salt        | string | Yes      | **Base64-encoded** salt generated for SRP        |
| srp_verifier    | string | Yes      | **Base64-encoded** verifier derived for SRP      |
| master_key_salt | string | Yes      | **Base64-encoded** salt generated for master key |

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**[Response Format](api_responses.md#register-user-user)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/user/register \
    -H "Content-Type: application/json" \
    -d '{
        "new_username": "123hashedUsername",
        "srp_salt": "base64Salt",
        "srp_verifier": "base64Verifier",
        "master_key_salt": "base64MasterSalt"
    }'
```

---

### Change Username (User)
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

**[Response Format](api_responses.md#change-username-user)**

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

---

### Delete User (User)
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

**[Response Format](api_responses.md#delete-user-user)**

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

---

### Health Check (User)
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

> **Note:** Password change operations use special "Password Change Sessions" that are distinct from regular login sessions. These sessions have limited lifetime (5 minutes) and limited request counts based on the number of password entries.

### Start Password Change (Password)
**Endpoint**
`POST /api/password/start`

**Description**
Begins the process of a password change, returning the user's validation details to create a password change session.

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

**[Response Format](api_responses.md#start-password-change-password)**

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

---

### Continue Password Change (Password)
**Endpoint**
`POST /api/password/auth`

**Description**
Completes the SRP authentication process by providing client ephemeral value and proof. Returns password change session details and server proof for verification. Also returns list of all data entry public IDs.

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

**[Response Format](api_responses.md#continue-password-change-password)**

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

---

### Complete Password Change (Password)
**Endpoint**
`POST /api/password/complete`

**Description**
Complete a password change. If all entries have been completed, the change is confirmed, and the old password details are erased.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the password change session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
```

**[Response Format](api_responses.md#complete-password-change-password)**

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

---

### Abort Password Change (Password)
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

> **Note:** This can be done on the password change session, but does not necessarily need to be.

**[Response Format](api_responses.md#abort-password-change-password)**

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

---

### Get Entry (Password)
**Endpoint**
`POST /api/password/get`

**Description**
Request the encrypted name and data for a given data entry, as well as its unique encryption data.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the password change session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| entry_public_id | string | Yes      | Public ID of the entry.                          |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**[Response Format](api_responses.md#get-entry-password)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/get \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Add New Encryption for Entry (Password)
**Endpoint**
`POST /api/password/update`

**Description**
Set the encrypted name and data for a given data entry, encrypted with the new master key. Also provide the new unique encryption data.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| session_id      | string | Yes      | The public ID of the password change session.    |
| request_number  | int    | Yes      | The number of this request on the password change session. |
| encrypted_data  | string | Yes      | **Base64-encoded** encrypted payload (see below) |

**Encryption Payload**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |
| entry_public_id | string | Yes      | Public ID of the entry.                          |
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

**[Response Format](api_responses.md#add-new-encryption-for-entry-password)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/password/update \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Health Check (Password)
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

> **Note:** Session endpoints create and manage regular "Login Sessions" that are used for most API operations.

### Start Auth (Session)
**Endpoint**
`POST /api/session/start`

**Description**
Request the details to create a new login session, including SRP details, master key salt, and server ephemeral value for SRP authentication.

**Parameters**
| Field           | Type   | Required | Description                                      |
|-----------------|--------|----------|--------------------------------------------------|
| username        | string | Yes      | Hash of the user's username.                     |

**[Response Format](api_responses.md#start-auth-session)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/start \
    -H "Content-Type: application/json" \
    -d '{
        "username": "123hashedUsername"
    }'
```

---

### Complete Auth (Session)
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
> **⚠️ CRITICAL:** Sessions with unlimited requests and time will never naturally expire, and must be manually purged using the [Delete Session](#delete-session-session) or [Clean Sessions](#clean-sessions-session) APIs.

**[Response Format](api_responses.md#complete-auth-session)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/session/auth \
    -H "Content-Type: application/json" \
    -d '{
        "username": "123hashedUsername",
        "auth_id": "abc123authId",
        "eph_val_a": "base64ClientEphemeral",
        "proof_val_m1": "base64ClientProof",
        "maximum_requests": 50,
        "expiry_time": 1800
    }'
```

---

### Delete Session (Session)
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

**[Response Format](api_responses.md#delete-session-session)**

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

---

### Clean Sessions (Session)
**Endpoint**
`POST /api/session/clean`

**Description**
Delete all of the user's existing auth sessions from the database, preventing further use.

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

**[Response Format](api_responses.md#clean-sessions-session)**

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

---

### Health Check (Session)
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

### Create Entry (Data)
**Endpoint**
`POST /api/data/create`

**Description**
Create a new password entry with encrypted name and data, and provide the unique encryption data.

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
| entry_name      | string | Yes      | The new encrypted entry name payload.            |
| entry_data      | string | Yes      | The new encrypted entry data payload.            |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_name length][entry_name bytes]
[4 bytes: entry_data length][entry_data bytes]
```

**[Response Format](api_responses.md#create-entry-data)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/data/create \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Edit Entry (Data)
**Endpoint**
`POST /api/data/edit`

**Description**
Edit the encrypted name and data for a given data entry, and provide the new unique encryption data.

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
| entry_public_id | string | Yes      | Public ID of the entry.                          |
| entry_name      | string | No       | The new encrypted entry name payload.            |
| entry_data      | string | No       | The new encrypted entry data payload.            |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
[4 bytes: entry_name length][entry_name bytes]
[4 bytes: entry_data length][entry_data bytes]
```

> **⚠️ CRITICAL:** A new nonce must be generated for each new encryption. The old nonce must not be reused.
> **Note:** If `entry_name` is omitted from the payload, the entry name is left unchanged.
> **Note:** If `entry_data` is omitted from the payload, the entry data is left unchanged.
> **Note:** At least one of `entry_name` or `entry_data` must be provided; otherwise the request is invalid.

**[Response Format](api_responses.md#edit-entry-data)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/data/edit \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Delete Entry (Data)
**Endpoint**
`POST /api/data/delete`

**Description**
Delete all stored data for a given data entry.

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
| entry_public_id | string | Yes      | Public ID of the entry.                          |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

> **Note:** A deleted entry is deleted fully. It cannot be recovered.

**[Response Format](api_responses.md#delete-entry-data)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/data/delete \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Get Entry (Data)
**Endpoint**
`POST /api/data/get`

**Description**
Retrieve all data for a given password entry.

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
| entry_public_id | string | Yes      | Public ID of the entry.                          |

**Encryption Encoding**
```
[4 bytes: username length][username bytes]
[4 bytes: entry_public_id length][entry_public_id bytes]
```

**[Response Format](api_responses.md#get-entry-data)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/data/get \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Get List (Data)
**Endpoint**
`POST /api/data/list`

**Description**
Retrieve a list of the public IDs of all password entries, along with their names.

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

**[Response Format](api_responses.md#get-list-data)**

**Example Request**
```bash
curl -X POST https://[API_BASE_URL]/api/data/list \
    -H "Content-Type: application/json" \
    -d '{
        "session_id": "abc123sessionId",
        "request_number": 5,
        "encrypted_data": "base64EncryptedPayload"
    }'
```

---

### Health Check (Data)
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
