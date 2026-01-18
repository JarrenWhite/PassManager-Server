# SRPUtils

## Innate
- **Safe Prime (N):** RFC 5054 4096-bit group (Appendix A)
- **Generator (g):** 5

## generate_ephemeral
In
srp_verifier: bytes (v)

Out
eph_public_b: bytes (B)
eph_private_b: bytes (b)

## compute_session_key
In
eph_val_a: bytes (A)
eph_public_b: bytes (B)
eph_private_b: bytes (b)
srp_verifier: bytes (v)

Out
session_key: bytes (K)

## verify_proof
In
eph_val_a: bytes (A)
eph_public_b: bytes (B)
session_key: bytes (K)
proof_val_m1: bytes (M1)

Out
server_proof_m2: bytes (M2)


---


# AESUtils

## aes_encrypt
In
key: bytes
nonce: bytes
plaintext: bytes
aad: bytes

Out
ciphertext: bytes
auth_tag: bytes

## aes_decrypt
In
key: bytes
nonce: bytes
ciphertext: bytes
auth_tag: bytes
aad: bytes

Out
plaintext: bytes
