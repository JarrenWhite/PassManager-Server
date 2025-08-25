# Database Schema


## User
id
username
verifier
srp_salt
login_sessions
secure_data


## LoginSession
id
public_id
session_key
request_count
maximum_requests
expiry_time
last_used


## SecureData
id
public_id
entry_name_cyphertext
entry_name_nonce
entry_name_auth_tag
entry_data_cyphertext
entry_data_nonce
entry_data_auth_tag
