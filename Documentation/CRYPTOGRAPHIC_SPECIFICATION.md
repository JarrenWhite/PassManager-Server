# Encryption Details

This document defines the cryptographic standards and implementation requirements for the password manager system.

## Hashing Requirements

**Algorithm:** SHA-256

### What Gets Hashed
- **Username:** Client must hash username before sending to server (never plaintext)
- **User Secret Keys:** Server stores only hashed versions of secret keys (never plaintext)

### Username Hashing Process
1. Convert username to UTF-8 bytes
2. Compute SHA-256 hash of UTF-8 bytes
3. Encode result as hex string for transmission

> **⚠️ CRITICAL:** Do not use a salt for the username's hash. This is used to identify the vault. This does mean that the username is less secure, and is more susceptible to rainbow attacks. This is seen as unavoidable without enforcing random login IDs.

## Encryption Requirements

**Algorithm:** AES-256-GCM

### What Gets Encrypted
- **User Secret Keys:** Client encrypts secret key before transmission
- **Password Entry Names:** Client encrypts password names separately from password entry data
- **Password Entry Data:** Client encrypts complete password entries before transmission

## Encryption Process

### Input Parameters
- **Encryption Key:** 32 bytes (256 bits) symmetric key
- **Nonce:** 12 bytes (96 bits), randomly generate for each encryption
- **Plaintext:** Data to be encrypted

### Output
- **Ciphertext:** Encrypted data
- **Authentication Tag:** 16 bytes (128 bits) for integrity verification

> **⚠️ CRITICAL:** Never reuse the same nonce with the same key

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

### User Secret Key Encryption
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

### Encoding Requirements
- **Byte Order:** Big-endian (network byte order) for all length fields
- **Length Field:** 4-byte unsigned integer (0 to 4,294,967,295)
- **Empty Fields:** Length 0, no data bytes
- **UTF-8 Validation:** All text fields must be valid UTF-8 sequences

### Pre-Encryption Encoding

The data must be encoded in this way prior to encryption:

#### Secret Key
```
Use raw 32-byte binary data directly (no encoding needed)
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

## Server Storage

Database stores for each encrypted Password Entry Data:
- **Nonce:** 12 bytes
- **Ciphertext:** variable length
- **Authentication Tag:** 16 bytes

## Decryption Process

### Input Parameters
- **Encryption Key:** Same 32 bytes (256 bits) key used for encryption
- **Nonce:** 12 bytes stored with encrypted data
- **Ciphertext:** Encrypted data from storage
- **Authentication Tag:** 16 bytes for integrity verification

### Output
- **Plaintext:** Original unencrypted data

### Process
Authentication tag is verified before decryption to ensure data integrity

## Additional Authenticated Data (AAD)

- **Status:** Not currently implemented
- **Future:** May be added for additional security context
