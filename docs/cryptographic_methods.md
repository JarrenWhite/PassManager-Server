# Encryption Details

This document defines the cryptographic standards and implementation requirements for the password manager system.

## Overview
1. **Hashing**
2. **Encryption Requirements**
3. **Encryption Process**
4. **Decryption Process**
5. **Session Key Derivation**
6. **Encryption Key Derivation**
7. **Specific Encryption Settings**
8. **Data Encoding**

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

### Output
- **Ciphertext:** Encrypted data
- **Authentication Tag:** 16 bytes (128 bits) for integrity verification

> **⚠️ CRITICAL:** Never reuse the same nonce with the same key.

---


## Decryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), stored with encrypted data
- **Ciphertext:** Encrypted data from storage
- **Authentication Tag:** 16 bytes (128 bits), for integrity verification

### Output
- **Plaintext:** Original unencrypted data

---


## Session Key Derivation

---


## Master Key Derivation

The master key is derived from the user password using a Key Derivation Function (KDF). It is used to encrypt and decrypt the user's password data. Therefore, it needs to be consistently determined across possible platforms and implementations. The key (and the password) **must never be sent to the server**.

### Algorithm & Parameters
- **KDF Algorithm:** Argon2id (`type=Argon2id`)
- **Time Cost:** 3 iterations
- **Memory Cost:** 65,536 KiB (64 MB)
- **Parallelism:** 1 thread
- **Key Length:** 32 bytes (256 bits)
- **Salt Size:** 32 bytes (generated randomly per user, per account)

### Input & Encoding
- Passwords must be UTF-8 encoded before being passed to Argon2id.

### Salt Handling
- Salts must be generated on the **client** using a **cryptographically secure random number generator**.
- Salts must be **unique per user** and **never reused**.
- Salts must be encoded safely (e.g., Base64) when stored or transmitted to the server.

> **⚠️ CRITICAL:** The password input **must never** be logged, cached, or transmitted.
> **⚠️ CRITICAL:** The master key **must never** be logged, cached, or transmitted.
> **⚠️ CRITICAL:** A new salt **must** be generated with each user creation. They **must** never be re-used.

---


## Specific Encryption Settings

### Request Data Encryption
- **Content:** The API request data.
- **Key:** Shared Session Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

### Password Names Encryption
- **Content:** The name for the password entry.
- **Key:** User Master Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

### Password Blob Encryption
- **Content:** The data for the password entry.
- **Key:** User Master Key.
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

> **Note:** Some cryptographic libraries combine ciphertext and auth tag, others return separately. These must be separated before being sent to the server.

---


## Data Encoding

### Encoding Requirements
- **Byte Order:** Big-endian (network byte order) for all length fields
- **Length Field:** 4-byte unsigned integer (0 to 4,294,967,295)
- **Empty Fields:** Length 0, no data bytes
- **UTF-8 Validation:** All text fields must be valid UTF-8 sequences

### Pre-Encryption Encoding

The data must be encoded in this way prior to encryption:

#### API Request Data
```
The encoding for each API request is specified in the API documentation.
```

#### Password Entry Name
```
[4 bytes: entry_name length][entry_name bytes]
```

#### Password Entry Data
```
[4 bytes: website length][website bytes]
[4 bytes: username length][username bytes]
[4 bytes: password length][password bytes]
[4 bytes: notes length][notes bytes]
```
