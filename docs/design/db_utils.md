# DBUtilsUser

## create
In
username_hash: str
srp_salt: str
srp_verifier: str
master_key_salt: str

## change_username
> Note: Halt if password change in progress

In
user_id: int
new_username_hash: str

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
eph_private_b: str
eph_public_b: str
expiry_time: datetime
srp_salt: str
srp_verifier: str
master_key_salt: str

Out
public_id: str

## complete
In
user_id: int

Out
public_ids: [str]

## abort
In
user_id: int

## update
In
public_id: str
entry_name: str
entry_data: str

## clean_password_change
"""Remove all partial password change entries, ephemerals and login sessions"""
In
db_session: Session
user: User

---


# DBUtilsAuth

## start
In
username_hash: str
eph_private_b: str
eph_public_b: str
expiry_time: datetime

Out
public_id: str
srp_salt: str

## get_details
In
public_id: str

Out
username_hash: str
user_id: int
eph_private_b: str
eph_public_b: str

## complete
In
public_id: str
session_key: str
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
entry_name: str
entry_data: str

Out
public_id: str

## edit
> Note: Halt if password change in progress

In
public_id: str
entry_name: str?
entry_data: str?

## delete
> Note: Halt if password change in progress

In
public_id: str

## get_entry
> Note: Halt if password change in progress

In
public_id: str

Out
entry_name: str
entry_data: str

## get_list
> Note: Halt if password change in progress

In
user_id: int

Out
{public_id: entry_name}: {str: str}


---


# DBUtilsSession

## get_details
In
public_id: str

Out
user_id: int
session_id: int
session_key: str
request_count: int
password_change: bool

## log_use
In
public_id: int

Out
session_key: str

## delete
In
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
