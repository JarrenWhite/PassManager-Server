# Database Schema


## User
**id:** Database ID for the entry
**username:** Hash of the user's username
**srp_salt:** The salt used to create the verifier in SRP
**srp_verifier:** The verifier used to create secure session keys using SRP
**master_key_salt:** The salt used to create the master key
**login_sessions:** List of all linked LoginSession entries
**secure_data:** List of all linked SecureData entries


## LoginSession
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**session_key:** Key used for session encryption and safety
**request_count:** Number of successful requests made on this session so far
**maximum_requests:** Number of requests after which the session will expire
**expiry_time:** Time past which the session will expire
**last_used:** Time at which the session was last used


## SecureData
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**entry_name:** Name for the password entry. Encrypted, and stored with nonce and auth_tag
**entry_data:** Data for the password entry. Encrypted, and stored with nonce and auth_tag
