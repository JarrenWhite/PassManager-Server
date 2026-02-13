# API Calls

A brief introduction to the API, its purpose, and how to make API calls.
([See API Responses](api_responses.md))

> **API Base URL:** `https://[GRPC_URL]`

> **TODO:** *Replace `[GRPC_URL]` and `[GRPC_PORT]` with the actual domain when determined*

## Overview
1. [**gRPC Details**](#grpc-details)
2. [**User**](#user)
    1. [Register User](#register-user-user)
    2. [Change Username](#change-username-user)
    3. [Delete User](#delete-user-user)
    4. [Health Check](#health-check-user)
3. [**Password**](#password)
    1. [Start Password Change](#start-password-change-password)
    2. [Continue Password Change](#continue-password-change-password)
    3. [Complete Password Change](#complete-password-change-password)
    4. [Abort Password Change](#abort-password-change-password)
    5. [Get Entry](#get-entry-password)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry-password)
    7. [Health Check](#health-check-password)
4. [**Session**](#session)
    1. [Start Auth](#start-auth-session)
    2. [Complete Auth](#complete-auth-session)
    3. [Delete Session](#delete-session-session)
    4. [Clean Sessions](#clean-sessions-session)
    5. [Health Check](#health-check-session)
5. [**Data**](#data)
    1. [Create Entry](#create-entry-data)
    2. [Edit Entry](#edit-entry-data)
    3. [Delete Entry](#delete-entry-data)
    4. [Get Entry](#get-entry-data)
    5. [Get List](#get-list-data)
    6. [Health Check](#health-check-data)

---


## gRPC Details

All calls to this server are made by RPC. Each RPC method takes a protobuf message as a request and returns a protobuf message in response.
The protobuf definitions can be found in the [protobuf definitions](https://github.com/JarrenWhite/PassManager-Protobufs) repository.
This documentation describes the RPC required to invoke each request, as well as the protobuf type of its request message.
The contents of that request message are further described in the entry's documentation.
For details of the response message, see ([API Responses](api_responses.md))

### Calling Details
Host: [GRPC_URL]
Port: [GRPC_PORT]
Protocol: HTTP/2

### Services
Version: v0

Services:
```
User:      passmanager.user.\<version\>.User
Password:  passmanager.password.\<version\>.Password
Session:   passmanager.session.\<version\>.Session
Data:      passmanager.data.\<version\>.Data
```

### Secure Messages:
Many RPC methods require a SecureRequest protobuf message and return a SecureResponse protobuf message.
These message types can be found in the `passmanager.common.\<version\>` package, within `secure.proto`.

These message types contain an `encrypted_data` field.
This field is populated with a payload protobuf message, encrypted using a shared session key.
Each request and response is associated with a specific payload protobuf message.
For these RPC methods, the message associated with the request is specified in the request's documentation.


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
| new_username    | bytes  | Yes      | Hash of the new username.                        |
| srp_salt        | bytes  | Yes      | Salt generated for SRP.                          |
| srp_verifier    | bytes  | Yes      | Verifier derived for SRP.                        |
| master_key_salt | bytes  | Yes      | Salt generated for master key.                   |

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**[Response Format](api_responses.md#register-user-user)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the original username.                   |
| new_username    | bytes  | Hash of the new username.                        |

> **Note:** Usernames should be enforced to be an email address, to reduce rainbow attack effectiveness.

**[Response Format](api_responses.md#change-username-user)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

> **Note:** The request number for this request type must be 0. This means a new session must be created for user deletion.

**[Response Format](api_responses.md#delete-user-user)**


---

### Health Check (User)
**Endpoint**
`GET /api/user/health`

**Description**
Check the health and availability of the User API endpoints. Returns system status information.

**Parameters**
None required.


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                           |
|-----------------|--------|-------------------------------------------------------|
| username_hash   | bytes  | Hash of the original username.                        |
| srp_salt        | bytes  | Salt generated for new SRP.                           |
| srp_verifier    | bytes  | Verifier derived for new SRP.                         |
| master_key_salt | bytes  | Salt generated for new master key.                    |

> **Note:** An existing auth session is required in order to start a password change auth session.

**[Response Format](api_responses.md#start-password-change-password)**


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
| encrypted_data   | bytes  | Yes      | Encrypted payload. (see below)                       |

**Encryption Payload**
| Field           | Type   | Description                                           |
|-----------------|--------|-------------------------------------------------------|
| username_hash   | bytes  | Hash of the original username.                        |
| auth_id         | string | Public ID of the AuthEphemeral being used.            |
| eph_val_a       | bytes  | Client ephemeral value. (A)                           |
| proof_val_m1    | bytes  | Client proof. (M1)                                    |

> **Note:** Password changing sessions expire after 5 minutes.

> **Note:** Password changing sessions have a limited number of requests based on the user's number of password entries. (Enough requests to read and write to each password once, with an additional request to complete the password change.)

> **Note:** A user can only have one active password changing session.

**[Response Format](api_responses.md#continue-password-change-password)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

**[Response Format](api_responses.md#complete-password-change-password)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

> **Note:** This can be done on the password change session, but does not necessarily need to be.

**[Response Format](api_responses.md#abort-password-change-password)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_public_id | string | Public ID of the entry.                          |

**[Response Format](api_responses.md#get-entry-password)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_public_id | string | Public ID of the entry.                          |
| entry_name      | bytes  | The new encrypted entry name payload.            |
| entry_data      | bytes  | The new encrypted entry data payload.            |

> **⚠️ CRITICAL:** The newly encrypted entry name and data must be encrypted using the new master key.

> **⚠️ CRITICAL:** A new nonce must be generated for each encryption. The old nonce must not be reused.

**[Response Format](api_responses.md#add-new-encryption-for-entry-password)**


---

### Health Check (Password)
**Endpoint**
`GET /api/password/health`

**Description**
Check the health and availability of the Password API endpoints. Returns system status information.

**Parameters**
None required.


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
| username_hash   | bytes  | Yes      | Hash of the user's username.                     |

> **Note:** Auth requests are valid for 180 seconds. Requests not completed within this time will be invalidated.

**[Response Format](api_responses.md#start-auth-session)**


---

### Complete Auth (Session)
**Endpoint**
`POST /api/session/auth`

**Description**
Completes the SRP authentication process by providing client ephemeral value and proof. Returns session details and server proof for verification.

**Parameters**
| Field            | Type   | Required | Description                                          |
|------------------|--------|----------|------------------------------------------------------|
| username_hash    | bytes  | Yes      | Hash of the user's username.                         |
| auth_id          | string | Yes      | Public ID of the AuthEphemeral being used.           |
| eph_val_a        | bytes  | Yes      | Client ephemeral value. (A)                          |
| proof_val_m1     | bytes  | Yes      | Client proof. (M1)                                   |
| maximum_requests | int    | No       | Number of requests before the session will expire.   |
| expiry_time      | int    | No       | Session expiry time in seconds from now.             |

> **Note:** If left blank, maximum requests will default to 100, and expiry time will default to 3600.

> **Note:** Maximum requests can be set to unlimited using a value of -1.

> **Note:** Expiry time can be set to unlimited using a value of -1.

> **⚠️ CRITICAL:** Sessions with unlimited requests and time will never naturally expire, and must be manually purged using the [Delete Session](#delete-session-session) or [Clean Sessions](#clean-sessions-session) APIs.

**[Response Format](api_responses.md#complete-auth-session)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                                      |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| session_id      | string | Public ID of the session to be deleted.          |

> **Note:** The session being deleted does not need to be the one in use.

> **Note:** Deleting a password change session this way will terminate the password change.

**[Response Format](api_responses.md#delete-session-session)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload (see below)                                       |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

> **Note:** The session being used to auth this request will also be deleted.

> **Note:** Deleting a password change session this way will terminate the password change.

**[Response Format](api_responses.md#clean-sessions-session)**


---

### Health Check (Session)
**Endpoint**
`GET /api/session/health`

**Description**
Check the health and availability of the Session API endpoints. Returns system status information.

**Parameters**
None required.


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_name      | bytes  | The new encrypted entry name payload.            |
| entry_data      | bytes  | The new encrypted entry data payload.            |

**[Response Format](api_responses.md#create-entry-data)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_public_id | string | Public ID of the entry.                          |
| entry_name      | bytes  | The new encrypted entry name payload.            |
| entry_data      | bytes  | The new encrypted entry data payload.            |

> **⚠️ CRITICAL:** A new nonce must be generated for each new encryption. The old nonce must not be reused.

> **Note:** If `entry_name` is omitted from the payload, the entry name is left unchanged.

> **Note:** If `entry_data` is omitted from the payload, the entry data is left unchanged.

> **Note:** At least one of `entry_name` or `entry_data` must be provided; otherwise the request is invalid.

**[Response Format](api_responses.md#edit-entry-data)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_public_id | string | Public ID of the entry.                          |

> **Note:** A deleted entry is deleted fully. It cannot be recovered.

**[Response Format](api_responses.md#delete-entry-data)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |
| entry_public_id | string | Public ID of the entry.                          |

**[Response Format](api_responses.md#get-entry-data)**


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
| encrypted_data  | bytes  | Yes      | Encrypted payload. (see below)                   |

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

**[Response Format](api_responses.md#get-list-data)**


---

### Health Check (Data)
**Endpoint**
`GET /api/data/health`

**Description**
Check the health and availability of the Data API endpoints. Returns system status information.

**Parameters**
None required.
