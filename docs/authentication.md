# Authentication

This document outlines the authentication and password management system for the PassManager system, using the Secure Remote Password (SRP) protocol for secure user authentication, session management, and password changes.

## Overview
1. [**Authentication Flow**](#authentication-flow)
2. [**Session Management**](#session-management)
3. [**Password Change Process**](#password-change-process)
4. [**Security Implementation**](#security-implementation)

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
**RCP Method:** `User.Register`

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

**RCP Methods:**
- `Session.Start` - Initiate authentication
- `Session.Auth` - Complete authentication

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
- **RPC Method:** `Password.Start`

#### 2. Continue Password Change
- **Requirement:** Active login session
- **Action:** Completes SRP authentication for new credentials
- **Result:** Returns session details and list of all entry public IDs
- **RPC Method:** `Password.Auth`

#### 3. Process Entries
- **Requirement:** Password change session
- **Action:** Request and update each entry with new encryption
- **Process:**
  - Request entry data
  - Update entry encryption
- **Constraint:** Must process all entries before completion
- **RPC Methods:** `Password.Get`, `Password.Update`

#### 4. Complete Password Change
- **Requirement:** All entries processed & Password change session
- **Action:** Finalises password change and cleans up
- **Result:** Old credentials erased, new credentials activated
- **RPC Method:** `Password.Complete`

#### 5. Abort Password Change (Optional)
- **Requirement:** Any active session
- **Action:** Cancels password change process
- **Result:** All temporary data removed, old credentials preserved
- **RPC Method:** `Password.Abort`

### Critical Security Requirements

> **⚠️ CRITICAL:** During password changes:
> - All other sessions for the user are invalidated
> - Non-password-change requests are ignored
> - New nonces must be generated for each encryption
> - Old nonces must never be reused
> - New master key must be used for all re-encryption
