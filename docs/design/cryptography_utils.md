# SRPUtils

## Innate
- **Safe Prime (N):** RFC 5054 4096-bit group (Appendix A)
- **Generator (g):** 5

## generate_ephemeral
In
srp_verifier: str (v)

Out
eph_public_b: str (B)
eph_private_b: str (b)

## compute_session_key
In
eph_val_a: str (A)
eph_public_b: str (B)
eph_private_b: str (b)
srp_verifier: str (v)

Out
session_key: str (K)

## verify_proof
In
eph_val_a: str (A)
eph_public_b: str (B)
session_key: str (K)
proof_val_m1: str (M1)

Out
server_proof_m2: str (M2)


---


# AESUtils

## aes_encrypt
In
key: str
nonce: str
plaintext: str
aad: str

Out
ciphertext: str
auth_tag: str

## aes_decrypt
In
key: str
nonce: str
ciphertext: str
auth_tag: str
aad: str

Out
plaintext: str
