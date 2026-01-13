# Authentication

This document outlines the authentication and password management system for the PassManager system, using the Secure Remote Password (SRP) protocol for secure user authentication, session management, and password changes.

## Overview
1. [**Authentication Flow**](#authentication-flow)
2. [**Session Management**](#session-management)
3. [**Password Change Process**](#password-change-process)
4. [**High-Risk Operations**](#high-risk-operations)
5. [**Security Implementation**](#security-implementation)

---


## Authentication Flow

### User Creation Process

```
1. Client chooses a password
2. Client generates a random salt
3. Client computes SRP verifier using password + salt
4. Client → Server: Send username, SRP verifier, and salt

5. Server stores username, verifier, and salt
6. Server → Client: Acknowledge successful user creation
```

**API Endpoint:** `POST /api/user/register`

### Session Creation Process

```
1. Client → Server: Request authentication for username

2. Server fetches user's salt and verifier
3. Server generates ephemeral server value (B)
4. Server → Client: Send salt and B

5. Client generates ephemeral client value (A)
6. Client computes shared session key (S) using password, salt, A, and B
7. Client computes client proof (M1) to prove knowledge of S
8. Client → Server: Send A and M1

9. Server computes shared session key (S) using verifier, A, and B
10. Server verifies client proof M1
11. Server → Client: Send server proof (M2) to confirm authentication

12. Client verifies server proof M2
```

**API Endpoints:**
- `POST /api/session/start` - Initiate authentication
- `POST /api/session/auth` - Complete authentication

### Request Authentication Process

```
1. Client fetches shared session key
2. Client fetches request count for this session
3. Client encrypts request + request count
4. Client → Server: Send username and encrypted request + request count

5. Server fetches shared session key for the username
6. Server decrypts request + request count
7. Server compares request count to stored request count for the session key
8. Server processes request and increments stored request count by 1
9. Server → Client: Send acknowledgment or response to the request
```

---


## Session Management

### Session Types

The system supports two distinct session types:

#### 1. **Login Sessions** (Regular)
- **Purpose:** Standard API operations (CRUD operations, user management)
- **Lifetime:** Configurable (default: 100 requests, 1 hour)
- **Authentication:** SRP protocol with session key derivation
- **Scope:** Full API access (except password change operations)

#### 2. **Password Change Sessions** (Special)
- **Purpose:** Exclusive to password change operations
- **Lifetime:** Fixed 5 minutes, limited request count
- **Authentication:** SRP protocol with special constraints
- **Scope:** Password change operations only

### Session Constraints

| Session Type | Max Requests | Expiry Time | Special Flags |
|--------------|--------------|-------------|---------------|
| Login Session | Configurable (default: 100) | Configurable (default: 1 hour) | `password_change: false` |
| Password Change | `(# entries × 2) + 1` | 5 minutes | `password_change: true` |

> **Note:** Password change sessions have limited requests to ensure they can only read/write each entry once.
Two for each data entry, plus one request to complete the change.

---


## Password Change Process

### Step-by-Step Process

#### 1. Start Password Change
- **Requirement:** Active login session
- **Action:** Creates special password change session
- **Result:** Returns validation details for new credentials
- **API:** `POST /api/password/start`

#### 2. Continue Password Change
- **Requirement:** Active login session
- **Action:** Completes SRP authentication for new credentials
- **Result:** Returns session details and list of all entry public IDs
- **API:** `POST /api/password/auth`

#### 3. Process Entries
- **Requirement:** Password change session
- **Action:** Request and update each entry with new encryption
- **Process:**
  - Request entry data: `POST /api/password/get`
  - Update entry encryption: `POST /api/password/update`
- **Constraint:** Must process all entries before completion

#### 4. Complete Password Change
- **Requirement:** All entries processed & Password change session
- **Action:** Finalises password change and cleans up
- **Result:** Old credentials erased, new credentials activated
- **API:** `POST /api/password/complete`

#### 5. Abort Password Change (Optional)
- **Requirement:** Any active session
- **Action:** Cancels password change process
- **Result:** All temporary data removed, old credentials preserved
- **API:** `POST /api/password/abort`

### Critical Security Requirements

> **⚠️ CRITICAL:** During password changes:
> - All other sessions for the user are invalidated
> - Non-password-change requests are ignored
> - New nonces must be generated for each encryption
> - Old nonces must never be reused
> - New master key must be used for all re-encryption

---


## High-Risk Operations

### Account Deletion

Account deletion is a high-risk, irreversible operation that permanently removes all user data. To ensure maximum security, account deletion enforces strict authentication requirements.

#### Security Requirements

**Password-Change Session Mandatory:**
- Account deletion **requires** a password-change session (not a regular login session)
- This ensures the user has recently verified their password before deletion
- The session must be fresh (request_count == 0)

**API Endpoint:** `POST /api/user/delete`

#### Why Password-Change Sessions?

Password-change sessions provide stronger security guarantees than regular login sessions:

1. **Recent Password Verification:** The user must have entered their password within the last 5 minutes
2. **Limited Lifetime:** Password-change sessions expire after 5 minutes (vs. 1 hour for regular sessions)
3. **Limited Scope:** These sessions cannot be used for normal operations, reducing attack surface
4. **Fresh Session Requirement:** The deletion must be the first request on the session (request_number = 0)

#### Implementation Pattern

```
1. User initiates password change flow: POST /api/password/start
2. User completes authentication: POST /api/password/auth
3. Server creates password-change session
4. User immediately requests account deletion: POST /api/user/delete
   - session_id: [password-change session ID]
   - request_number: 0
5. Server validates:
   - Session exists and is valid
   - Session has password_change flag set to True
   - request_count == 0 (fresh session)
6. If all checks pass, account is deleted
```

#### Error Responses

| Condition | Error Code | HTTP Status | Message |
|-----------|------------|-------------|---------|
| Regular session used | `ltd03` | 412 | Account deletion requires a password-change session |
| Request count != 0 | `ltd01` | 400 | Request number must be 0 for this request type |
| Session not found | `gnr01` | 404 | session_id not found |

---
