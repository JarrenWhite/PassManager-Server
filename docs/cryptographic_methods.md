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



## Decryption Process



## Session Key Derivation



## Encryption Key Derivation



## Session Key Derivation



## Encryption Key Derivation



## Specific Encryption Settings



## Data Encoding

