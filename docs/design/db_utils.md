# DBUtilsUser

## create
In
username_hash: bytes
srp_salt: bytes
srp_verifier: bytes
master_key_salt: bytes

## change_username
> Note: Halt if password change in progress

In
user_id: int
new_username_hash: bytes

## delete
> Note: Halt if password change in progress

In
user_id: int


---


# DBUtilsPassword

## start
> Note: Halt if password change in progress

In
user_id: int
eph_private_b: bytes
eph_public_b: bytes
expiry_time: datetime
srp_salt: bytes
srp_verifier: bytes
master_key_salt: bytes

Out
public_id: str

## complete
> Note: Risk of Insecure Direct Object Reference

In
user_id: int
public_id: str
session_key: bytes
expiry_time: datetime

Out
public_id: str

## commit
In
user_id: int

Out
public_ids: [str]

## abort
In
user_id: int

## update
> Note: Risk of Insecure Direct Object Reference

In
user_id: int
public_id: str
entry_name: bytes
entry_data: bytes

## clean_password_change
"""Remove all partial password change entries, ephemerals and login sessions"""
In
db_session: Session
user: User


---


# DBUtilsAuth

## start
In
username_hash: bytes
eph_private_b: bytes
eph_public_b: bytes
expiry_time: datetime

Out
public_id: str
srp_salt: bytes

## get_details
> Note: Risk of Insecure Direct Object Reference

In
user_id: int
public_id: str

Out
username_hash: bytes
user_id: int
eph_private_b: bytes
eph_public_b: bytes

## complete
In
public_id: str
session_key: bytes
maximum_requests: int?
expiry_time: datetime?

Out
public_id: str

## clean_all
()

## _check_expiry
In
db_session: Session
auth_ephemeral: AuthEphemeral


---


# DBUtilsData

## create
> Note: Halt if password change in progress

In
user_id: int
entry_name: bytes
entry_data: bytes

Out
public_id: str

## edit
> Note: Risk of Insecure Direct Object Reference
> Note: Halt if password change in progress

In
user_id: int
public_id: str
entry_name: bytes?
entry_data: bytes?

## delete
> Note: Risk of Insecure Direct Object Reference
> Note: Halt if password change in progress

In
user_id: int
public_id: str

## get_entry
> Note: Halt if password change in progress
> Note: Risk of Insecure Direct Object Reference

In
user_id: int
public_id: str

Out
entry_name: bytes
entry_data: bytes

## get_list
> Note: Halt if password change in progress

In
user_id: int

Out
{public_id: entry_name}: {str: bytes}


---


# DBUtilsSession

## get_details
In
public_id: str

Out
user_id: int
username_hash: bytes
session_id: int
session_key: bytes
request_count: int
password_change: bool

## log_use
In
public_id: int

Out
session_key: bytes

## delete
> Note: Risk of Insecure Direct Object Reference

In
user_id: int
public_id: str

## clean_user
In
user_id: int

## clean_all
()

## _check_expiry
In
db_session: Session
login_session: LoginSession
