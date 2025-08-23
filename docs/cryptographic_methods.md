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



## Hashing

**Algorithm:** SHA-256

### What Gets Hashed:
**Username:** Client must hash username before sending to server (never plaintext)

### Username Hashing Process
1. Convert username to UTF-8 bytes
2. Compute SHA-256 hash of UTF-8 bytes
3. Encode result as hex string for transmission

> **⚠️ CRITICAL:** Do not use a salt for the username's hash. This is used to identify the vault. This does mean that the username is less secure, and is more susceptible to rainbow attacks. This is seen as unavoidable without enforcing random login IDs.



## Encryption Requirements

**Algorithm:** AES-256-GCM

### What Gets Encrypted:
**API Request Data:** Client encrypts API request data using the shared session key.
**Password Entry Names:** Client encrypts password entry names using password-derived key.
**Password Entry Data:** Client encrypts password entry data using password-derived key.



## Encryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), randomly generate for each encryption
- **Plaintext:** Data to be encrypted

### Output
- **Ciphertext:** Encrypted data
- **Authentication Tag:** 16 bytes (128 bits) for integrity verification

> **⚠️ CRITICAL:** Never reuse the same nonce with the same key



## Decryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), stored with encrypted data
- **Ciphertext:** Encrypted data from storage
- **Authentication Tag:** 16 bytes (128 bits), for integrity verification

### Output
- **Plaintext:** Original unencrypted data



## Session Key Derivation



## Encryption Key Derivation

The encryption key is derived from user password using a Key Derivation Function (KDF):

- **Algorithm:** Argon2id
- **Parameters:**
  - `memory_cost=65536`
  - `time_cost=3`
  - `parallelism=1`
- **Salt:** Random value used in key derivation (32 bytes)
- **Key Length:** 32 bytes (256 bits)
- **Salt Storage:** Send salt to server for secure storage



## Specific Encryption Settings

### Request Data Encryption
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

### Password Blob Encryption
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

### Password Names Encryption
- **Process:** Encrypt password names separately from password data
- **Settings:** AES-256-GCM with 12-byte nonce, 16-byte auth tag
- **Server Payload:** `nonce` (12 bytes), `ciphertext` (variable), `auth_tag` (16 bytes)

> **Note:** Some cryptographic libraries combine ciphertext and auth tag, others return separately. These must be separated before being sent to the server.



## Data Encoding

