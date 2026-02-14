# API Responses

A brief introduction to the possible responses for all defined APIs.
([See API Requests](api_calls.md))

## Overview
1. [**Parsing Responses**](#parsing-responses)
2. [**User**](#user)
    1. [Register User](#register-user-user)
    2. [Change Username](#change-username-user)
    3. [Delete User](#delete-user-user)
3. [**Password**](#password)
    1. [Start Password Change](#start-password-change-password)
    2. [Continue Password Change](#continue-password-change-password)
    3. [Complete Password Change](#complete-password-change-password)
    4. [Abort Password Change](#abort-password-change-password)
    5. [Get Entry](#get-entry-password)
    6. [Add New Encryption for Entry](#add-new-encryption-for-entry-password)
4. [**Session**](#session)
    1. [Start Auth](#start-auth-session)
    2. [Complete Auth](#complete-auth-session)
    3. [Delete Session](#delete-session-session)
    4. [Clean Sessions](#clean-sessions-session)
5. [**Data**](#data)
    1. [Create Entry](#create-entry-data)
    2. [Edit Entry](#edit-entry-data)
    3. [Delete Entry](#delete-entry-data)
    4. [Get Entry](#get-entry-data)
    5. [Get List](#get-list-data)
6. [**Errors**](#errors)
    1. [Error Messages](#error-messages)
    2. [Request Errors](#request-errors)
    3. [General Field Errors](#general-field-errors)
    4. [Limited API Errors](#limited-api-errors)
    5. [HTTP Status Codes](#http-status-codes)

---

## Parsing Responses

### Success Detection
All response protobuf messages contain a `success` field, which is a bool.
The bool indicates whether the call was successful, or if it failed.

### Successful Message
If the call was successful, the `success_data` field will be populated.
The data contained in the documented `Response Fields` for each of the API Responses is within that `success_data`.

### Failed Message
If the call fails, the `failure_data` field will be populated.
The `failure_data` field contains the Failure protobuf message.
That message, and its contents, are further defined in the [Errors](#errors) section of this document.

### Secure Message
If the message was issued as part of a secured session, the response will be included in a SecureResponse protobuf message `passmanager.common.v#.SecureResponse`. This message will contain a `success` flag, and either `success_data` or `failure_data`, as with any other message. However, if successful, the `success_data` field will contain the fields `session_id` and `encrypted_data`.

`session_id` gives a reference to the session which this message was secured with, to allow the client to find the relevant session key for decryption.

`encrypted_data` contains a protobuf message which has been encrypted using the shared session key.
The type of the encrypted message is defined for each response in the documentation below.
Messages which use a secure message response are shown in the documentation by describing their **Encryption Payload** rather than their **Response Fields**.


## User

### Register User (User)

**[Request Format](api_calls.md#register-user-user)**

**Protobuf Messages**
`passmanager.user.v#.RegisterResponse`

**Response Fields**
| Field           | Type     | Description                                |
|-----------------|----------|--------------------------------------------|
| username_hash   | bytes    | Hash of the username that was registered.  |

---

### Change Username (User)

**[Request Format](api_calls.md#change-username-user)**

**Protobuf Messages**
`passmanager.user.v#.UserUsernameResponse`

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| new_username    | bytes  | Hash of the new username.                        |

---

### Delete User (User)

**[Request Format](api_calls.md#delete-user-user)**

**Protobuf Messages**
`passmanager.user.v#.UserDeleteResponse`

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---


## Password

### Start Password Change (Password)

**[Request Format](api_calls.md#start-password-change-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordStartResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| auth_id         | string   | The public ID of the in progress auth request.               |
| srp_salt        | bytes    | The salt used to create the verifier in SRP.                 |
| eph_public_b    | bytes    | Unique server ephemeral value (B) for this SRP auth attempt. |

---

### Continue Password Change (Password)

**[Request Format](api_calls.md#continue-password-change-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordAuthResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| session_id      | string   | The public ID of the created password session.               |
| server_proof_m2 | bytes    | The server's proof of authentication.                        |
| entry_ids       | [string] | The public IDs of all stored data entries.                   |

---

### Complete Password Change (Password)

**[Request Format](api_calls.md#complete-password-change-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordCompleteResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |

---

### Abort Password Change (Password)

**[Request Format](api_calls.md#abort-password-change-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordAbortResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |

---

### Get Entry (Password)

**[Request Format](api_calls.md#get-entry-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordGetResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |
| entry_name      | bytes    | Encrypted entry name payload.                                |
| entry_data      | bytes    | Encrypted entry data payload.                                |

---

### Add New Encryption for Entry (Password)

**[Request Format](api_calls.md#add-new-encryption-for-entry-password)**

**Protobuf Messages**
`passmanager.password.v#.PasswordUpdateResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---


## Session

### Start Auth (Session)

**[Request Format](api_calls.md#start-auth-session)**

**Protobuf Messages**
`passmanager.session.v#.SessionStartResponse`

**Response Fields**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| auth_id         | string   | The public ID of the in progress auth request.               |
| srp_salt        | bytes    | The salt used to create the verifier in SRP.                 |
| eph_public_b    | bytes    | Unique server ephemeral value (B) for this SRP auth attempt. |
| master_key_salt | bytes    | The salt used to create the master key.                      |

---

### Complete Auth (Session)

**[Request Format](api_calls.md#complete-auth-session)**

**Protobuf Messages**
`passmanager.session.v#.SessionAuthResponse`

**Response Fields**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| session_id      | string   | The public ID of the created session.                        |
| server_proof_m2 | bytes    | The server's proof of authentication.                        |

---

### Delete Session (Session)

**[Request Format](api_calls.md#delete-session-session)**

**Protobuf Messages**
`passmanager.session.v#.SessionDeleteResponse`

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---

### Clean Sessions (Session)

**[Request Format](api_calls.md#clean-sessions-session)**

**Protobuf Messages**
`passmanager.session.v#.SessionCleanResponse`

**Encryption Payload**
| Field           | Type   | Description                                      |
|-----------------|--------|--------------------------------------------------|
| username_hash   | bytes  | Hash of the user's username.                     |

---


## Data

### Create Entry (Data)

**[Request Format](api_calls.md#create-entry-data)**

**Protobuf Messages**
`passmanager.data.v#.DataCreateResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Edit Entry (Data)

**[Request Format](api_calls.md#edit-entry-data)**

**Protobuf Messages**
`passmanager.data.v#.DataEditResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Delete Entry (Data)

**[Request Format](api_calls.md#delete-entry-data)**

**Protobuf Messages**
`passmanager.data.v#.DataDeleteResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |

---

### Get Entry (Data)

**[Request Format](api_calls.md#get-entry-data)**

**Protobuf Messages**
`passmanager.data.v#.DataGetResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_public_id | string   | Public ID of the entry.                                      |
| entry_name      | bytes    | Encrypted entry name payload.                                |
| entry_data      | bytes    | Encrypted entry data payload.                                |

---

### Get List (Data)

**[Request Format](api_calls.md#get-list-data)**

**Protobuf Messages**
`passmanager.data.v#.DataGListResponse`

**Encryption Payload**
| Field           | Type     | Description                                                  |
|-----------------|----------|--------------------------------------------------------------|
| username_hash   | bytes    | Hash of the user's username.                                 |
| entry_ids       | [bytes]  | The public IDs of all stored data entries.                   |
| entry_names     | [bytes]  | The name payload for all stored data entries.                |

---


## Errors

### Error Messages

A failed RPC Method call returns a Failure protobuf message, which contains a list of Error protobuf messages, `error_list`.
Each Error protobuf contains a `field`, a `code` and a `description` entry.

- The `field` relates to the calling field that is at fault. Further described below.
- The `code` is stable and intended for programmatic handling.
- The `description` message is human-readable and is subject to change. It should be used for logging and debugging only.

> Note: Multiple errors may be returned in a single response. Clients should iterate through all Errors in the `error_list`.

### Protobuf Messages
Failure: `passmanager.common.v#.Failure`
Error: `passmanager.common.v#.Error`
ErrorCode: `passmanager.common.v#.ErrorCode`


### Error Code Scheme:
- `RQSXX`: Request-level errors that apply to the entire request.
- `SVRXX`: Server-level errors that apply to the application.
- `GNRXX`: General field errors that can apply to multiple APIs/fields.
- `OPRXX`: Operation specific errors that apply to limited endpoints only.


### Request Errors

These errors can be returned to any possible request.

| Error Code | Field           | Error Message                                                |
|------------|-----------------|--------------------------------------------------------------|
| RQS00      | request         | Incorrect parameters. Required: [\<fields\>]                 |
| RQS01      | request         | Failed to decrypt payload, invalid session or corrupted data |
| RQS02      | request         | Password change in progress                                  |
| RQS03      | request         | Too many requests                                            |
| SVR00      | server          | Server encountered an unexpected error                       |
| SVR01      | server          | Temporary outage/maintenance                                 |


### General Field Errors

These can be returned in response to multiple possible input fields.
Here, `Field` is defined by the name of protobuf message field.

| Error Code | Error message       |
|------------|---------------------|
| GNR00      | \<Field\> invalid   |
| GNR01      | \<Field\> not found |


### Operation Specific Errors

These errors are specific to certain APIs. Only those APIs can return these errors.

| Error Code | Field           | APIs | Error Message                                                |
|------------|-----------------|------|--------------------------------------------------------------|
| OPR00      | username_hash   | [Register User](#register-user-user) [Change Username](#change-username-user) | New username already exists |
| OPR01      | request_number  | [Delete User](#delete-user-user) | Request number must be 0 for this request type                   |
| OPR02      | request         | [Complete Password Change](#complete-password-change-password) | Password change is not complete                     |
