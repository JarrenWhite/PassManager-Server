# Authentication Specification

This document outlines the complete authentication flow for the PassManager system, utilizing the Secure Remote Password (SRP) protocol for secure user authentication and session management.

## Overview

The authentication system consists of three main processes:
1. [**User Creation Process**](#user-creation-process)
2. [**Session Creation Process**](#session-creation-process)
3. [**Request Authentication Process**](#request-authentication-process)

---


## User Creation Process

```
1. Client chooses a password
2. Client generates a random salt
3. Client computes SRP verifier using password + salt
4. Client → Server: Send username, SRP verifier, and salt

5. Server stores username, verifier, and salt
6. Server → Client: Acknowledge successful user creation
```

---


## Session Creation Process

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

---


## Request Authentication Process

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
