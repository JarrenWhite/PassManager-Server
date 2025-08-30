# Encryption Details

This document defines the cryptographic standards and implementation requirements for the password manager system.

## Overview
1. [**Hashing**](#hashing)
2. [**Encryption Requirements**](#encryption-requirements)
3. [**Encryption Process**](#encryption-process)
4. [**Decryption Process**](#decryption-process)
5. [**Master Key Derivation**](#master-key-derivation)
6. [**Session Key Derivation**](#session-key-derivation)
7. [**Specific Encryption Settings**](#specific-encryption-settings)
8. [**Data Encoding**](#data-encoding)

---


## Hashing

**Algorithm:** SHA-256

### What Gets Hashed:
**Username:** Client must hash username before sending to server (never plaintext)

### Username Hashing Process
1. Convert username to UTF-8 bytes
2. Compute SHA-256 hash of UTF-8 bytes
3. Encode result as hex string for transmission

> **⚠️ CRITICAL:** Do not use a salt for the username's hash. This is used to identify the vault. This does mean that the username is less secure, and is more susceptible to rainbow attacks. This is seen as unavoidable without enforcing random login IDs.

---


## Encryption Requirements

**Algorithm:** AES-256-GCM

### What Gets Encrypted:
**API Request Data:** Client encrypts API request data using the shared session key.
**Password Entry Names:** Client encrypts password entry names using password-derived key.
**Password Entry Data:** Client encrypts password entry data using password-derived key.

---


## Encryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), randomly generate for each encryption
- **Plaintext:** Data to be encrypted
- **AAD (Optional):** The AAD (Additional Authenticated Data) adds integrity protection. It is currently only used for API requests (specified in the Data Encoding).

### Output
- **Ciphertext:** Encrypted data
- **Authentication Tag:** 16 bytes (128 bits) for integrity verification

> **⚠️ CRITICAL:** Never reuse the same nonce with the same key.
> **Note:** The AAD information is not encrypted. It is used for integrity protection, and can be viewed by anyone with access to the packet.

---


## Decryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), stored with encrypted data
- **Ciphertext:** Encrypted data from storage
- **Authentication Tag:** 16 bytes (128 bits), for integrity verification
- **AAD (Optional):** This is only required where it was used in the encryption. Currently, that only includes API requests.

### Output
- **Plaintext:** Original unencrypted data

---


## Master Key Derivation

The master key is derived from the user password using a Key Derivation Function (KDF). It is used to encrypt and decrypt the user's password data. Therefore, it needs to be consistently determined across possible platforms and implementations. The key (and the password) **must never be sent to the server**.

### Algorithm & Parameters
- **KDF Algorithm:** Argon2id (`type=Argon2id`)
- **Time Cost:** 3 iterations
- **Memory Cost:** 65,536 KiB (64 MB)
- **Parallelism:** 1 thread
- **Salt Size:** 32 bytes (generated randomly per user, per password)
- **Key Length:** 32 bytes (256 bits)

### Input & Encoding
- Passwords must be UTF-8 encoded before being passed to Argon2id.

### Salt Handling
- Salts must be generated on the **client** using a **cryptographically secure random number generator**.
- Salts must be **unique per user** and **never reused**.
- Salts must be encoded safely (e.g., Base64) when stored or transmitted to the server.

> **⚠️ CRITICAL:** The password input **must never** be logged, cached, or transmitted.
> **⚠️ CRITICAL:** The master key **must never** be logged, cached, or transmitted.
> **⚠️ CRITICAL:** A new salt **must** be generated with each user creation. They **must** never be re-used.

### Reference Implementations
#### Python
```
from argon2.low_level import hash_secret_raw, Type
import os

def derive_master_key(password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )
```

#### JavaScript
```
import { argon2id } from "argon2";

const deriveMasterKey = async (password, salt) => {
  return await argon2id({
    password: new TextEncoder().encode(password),
    salt: salt,
    timeCost: 3,
    memoryCost: 65536,
    parallelism: 1,
    hashLength: 32,
    raw: true // ensures a raw key instead of encoded string
  });
};
```

---


## Session Key Derivation

### Algorithm & Parameters
- **SRP Algorithm:** SRP-6a
- **Hash Function:** SHA-256
- **Safe Prime (N):** 4096
- **Generator (g):** 5
- **Salt Size:** 32 bytes (generated randomly per user, per password)
- **Key Length:** 32 bytes (256 bits)

### Input & Encoding
- Username and Password must be UTF-8 encoded before being used in SRP-6a.
- Username and Password encoding must be normalised using NFKC before being used in SRP-6a.

### SRP Verifier Generation (User Registration)
During user registration, the client must generate an SRP verifier:
- Compute `x = hash(salt || hash(username ":" password))`
  - Where `||` is byte concatenation, and `":"` is the ASCII colon
- Interpret the hash output as big-endian integer
- Compute `verifier = g^x mod N`
- Send the salt and verifier to the server for storage

### Client Side Steps (Session Creation)
1. **Receive server ephemeral (B) and salt from server**
2. **Generate client ephemeral (A):**
   - Generate random private value `a` (320 bits)
   - Compute `A = g^a mod N`
3. **Compute scrambling parameter (u):**
   - `u = hash(A || B)` where `||` is byte concatenation
   - Interpret hash output as big-endian integer
4. **Compute session key (S):**
   - Compute `x = hash(salt || hash(username ":" password))`
   - Compute `S = (B - k*g^x)^(a + u*x) mod N`
   - Where `k = hash(N || g)` (SRP-6a multiplier)
5. **Derive shared session key:**
   - `K = hash(S)` - This becomes the 32-byte session key for API encryption

### Server Side Steps (Session Creation)
1. **Lookup user verifier (v) and salt from database**
2. **Generate server ephemeral (B):**
   - Generate random private value `b` (320 bits)
   - Compute `k = hash(N || g)` (SRP-6a multiplier)
   - Compute `B = k*v + g^b mod N`
3. **Send B and salt to client, receive A from client**
4. **Compute scrambling parameter (u):**
   - `u = hash(A || B)` where `||` is byte concatenation
   - Interpret hash output as big-endian integer
5. **Compute session key (S):**
   - Compute `S = (A * v^u)^b mod N`
6. **Derive shared session key:**
   - `K = hash(S)` - This becomes the 32-byte session key for API encryption

### Proof Generation & Verification
**Client generates proof (M1):**
- `M1 = hash(A || B || K)`

**Server verifies M1 and generates proof (M2):**
- Verify received M1 matches computed `hash(A || B || K)`
- Generate `M2 = hash(A || M1 || K)`
- Send M2 to client

**Client verifies M2:**
- Verify received M2 matches computed `hash(A || M1 || K)`

### Critical Security Requirements
> **⚠️ CRITICAL:** Private values `a` and `b` must be generated using cryptographically secure random number generators.
> **⚠️ CRITICAL:** Private values `a` and `b` must never be logged, cached, or transmitted.
> **⚠️ CRITICAL:** Session key `K` must never be logged or transmitted in plaintext.
> **⚠️ CRITICAL:** All computations must use constant-time operations where possible to prevent timing attacks.

---


## Specific Encryption Settings

### Request Data Encryption
- **Content:** The API request data.
- **Key:** Shared Session Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `auth_tag` (16 bytes), `ciphertext` (variable)
- **Server Payload Form:**
```[12 bytes: nonce][16 bytes: auth_tag][cyphertext...]```

### Password Names Encryption
- **Content:** The name for the password entry.
- **Key:** User Master Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `auth_tag` (16 bytes), `ciphertext` (variable)
- **Server Payload Form:**
```[12 bytes: nonce][16 bytes: auth_tag][cyphertext...]```

### Password Blob Encryption
- **Content:** The data for the password entry.
- **Key:** User Master Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `auth_tag` (16 bytes), `ciphertext` (variable)
- **Server Payload Form:**
```[12 bytes: nonce][16 bytes: auth_tag][cyphertext...]```

> **Note:** Some cryptographic libraries combine ciphertext and auth tag, others return separately. These must be correctly arranged before being sent to the server.

---


## Data Encoding

### Encoding Requirements
- **Byte Order:** Big-endian (network byte order) for all length fields
- **Length Field:** 4-byte unsigned integer (0 to 4,294,967,295)
- **Empty Fields:** Length 0, no data bytes
- **UTF-8 Validation:** All text fields must be valid UTF-8 sequences

### API Requests
The encoding for the content data of each API request is specified in the API documentation.
The AAD data is to be encoded as follows:
```
[4 bytes: request_number length][request_number bytes]      → Monotonic counter for this session (prevents replay attacks)
[4 bytes: session_id length][session_id]                    → Unique public identifier for the active session
```

### API Responses
The encoding for the content data of each API response is specified in the API documentation.
The AAD data is to be encoded as follows:
```
[4 bytes: session_id length][session_id]                    → Unique public identifier for the active session
```

### Password Entry Encoding

The password entries are encoded separately before encryption.

#### Password Entry Name
```
[4 bytes: entry_name length][entry_name bytes]              → Name of the password entry
```

#### Password Entry Data
```
[4 bytes: website length][website bytes]                    → Website the entry related to
[4 bytes: username length][username bytes]                  → Username of the given entry
[4 bytes: password length][password bytes]                  → Password of the given entry
[4 bytes: notes length][notes bytes]                        → Any notes for the entry
```
