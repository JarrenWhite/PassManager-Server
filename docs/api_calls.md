# API Calls

A brief introduction to the API, its purpose, and how to make API calls.

> **API Base URL:** `https://[API_BASE_URL]`  
> **TODO:** *Replace `[API_BASE_URL]` with the actual domain when determined*

## Base URL
```https://[API_BASE_URL]```

## API Structure
API endpoints follow the pattern: `/api/{type}/{callName}`

Where:
- `{type}` can be: `user`, `session`, `data`
- `{callName}` is the specific endpoint name

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


change username - TODO
change password (future) - TODO
delete user - TODO
health check - TODO

---


## Session

start auth - TODO
complete auth - TODO
delete session - TODO
clean sessions - TODO
health check - TODO

---


## Data

create entry - TODO
edit entry - TODO
delete entry - TODO
retrieve list - TODO
retrieve entry - TODO
health check - TODO
