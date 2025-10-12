# Database Schema

This document defines the database schema used within the password manager, as well as giving details about the various stored items.

## Overview
1. [User](#user)
2. [AuthEphemeral](#auth-ephemeral)
3. [LoginSession](#login-session)
4. [SecureData](#secure-data)

## User

### Purpose
Store main user information, including SRP authentication data, salts for encryption, and references to user sessions and data.

### **Columns**

| Column                  | Type      | Constraints                     |
|-------------------------|-----------|---------------------------------|
| **id**                  | BIGINT    | **Primary Key**                 |
| **username_hash**       | BLOB      | **Unique**, **Indexed**         |
| **srp_salt**            | BLOB      |                                 |
| **srp_verifier**        | BLOB      |                                 |
| **master_key_salt**     | BLOB      |                                 |
| **password_change**     | BOOL      |                                 |
| **new_srp_salt**        | BLOB      | **nullable**                    |
| **new_srp_verifier**    | BLOB      | **nullable**                    |
| **new_master_key_salt** | BLOB      | **nullable**                    |

### **Relationships**
- **AuthEphemeral** -> `AuthEphemeral.user_id` (one-to-many) cascading delete
- **LoginSession** → `LoginSession.user_id` (one-to-many) cascading delete
- **SecureData** → `SecureData.user_id` (one-to-many) cascading delete

### Column Descriptions
**id:** Database ID for the entry
**username_hash:** Hash of the user's username
**srp_salt:** The salt used to create the verifier in SRP
**srp_verifier:** The verifier used to create secure session keys using SRP
**master_key_salt:** The salt used to create the master key
**login_session:** List of all linked LoginSession entries
**secure_data:** List of all linked SecureData entries
**password_change:** Flag representing whether the user is currently undergoing a password change
**new_srp_salt:** Temporary store for new srp salt, while changing password
**new_srp_verifier:** Temporary store for new srp verifier name, while changing password
**new_master_key_salt:** Temporary store for new master key salt, while changing password

---


## AuthEphemeral

### Purpose
Tracks server ephemeral values (B) for each SRP authentication attempt to prevent replay attacks.

### **Columns**

| Column              | Type      | Constraints / Notes                              |
|---------------------|-----------|--------------------------------------------------|
| **id**              | BIGINT    | **Primary Key**, auto-increment                  |
| **public_id**       | CHAR(36)  | **Indexed**                                      |
| **eph_private_b**   | CHAR(36)  |                                                  |
| **eph_public_b**    | BLOB      |                                                  |
| **user_id**         | BIGINT    | **Foreign Key** → `User.id`                      |
| **expiry_time**     | TIMESTAMP | When the ephemeral value expires                 |
| **password_change** | BOOL      |                                                  |

### **Relationships**
- Belongs to **User** → `user_id`

### Column Descriptions
**id:** Database ID for the entry
**eph_private_b:** Randomly generated salt value (b) for this SRP auth attempt
**eph_public_b:** Unique server ephemeral value (B) for this SRP auth attempt
**user_id:** The user that the AuthEphemeral is associated with
**expires_at:** Timestamp when the ephemeral value expires (2 minutes from creation)
**password_change:** Flag indicating whether the ephemeral is for use with a password change action

---


## LoginSession

### Purpose
Tracks user authentication sessions, storing session keys and related data.

### **Columns**

| Column               | Type      | Constraints / Notes                       |
|----------------------|-----------|-------------------------------------------|
| **id**               | BIGINT    | **Primary Key**, auto-increment           |
| **public_id**        | CHAR(36)  | **Unique**, **Indexed**                   |
| **user_id**          | BIGINT    | **Foreign Key** → `User.id`               |
| **session_key**      | BLOB      |                                           |
| **request_count**    | INT       |                                           |
| **last_used**        | TIMESTAMP |                                           |
| **maximum_requests** | INT       | **nullable**                              |
| **expiry_time**      | TIMESTAMP | **nullable**                              |
| **password_change**  | BOOL      |                                           |

### **Relationships**
- Belongs to **User** → `user_id`

### Column Descriptions
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**user_id:** The user that the LoginSession is associated with
**session_key:** Key used for session encryption and safety. Encrypted with database_key, and stored with nonce and auth_tag
**request_count:** Number of successful requests made on this session so far (Counting from 0)
**maximum_requests:** Number of requests after which the session will expire
**expiry_time:** Time past which the session will expire
**last_used:** Time at which the session was last used
**password_change:** Flag indicating whether the session is for use with a password change action

---


## SecureData

### Purpose
Stores encrypted password entries, and related nonce and auth_tag for decryption.

| Column                 | Type      | Constraints / Notes                       |
|------------------------|-----------|-------------------------------------------|
| **id**                 | BIGINT    | **Primary Key**, auto-increment           |
| **public_id**          | CHAR(36)  | **Unique**, **Indexed**                   |
| **user_id**            | BIGINT    | **Foreign Key** → `User.id`, **Indexed**  |
| **entry_name**         | BLOB      |                                           |
| **entry_data**         | BLOB      |                                           |
| **new_entry_name**     | BLOB      | **nullable**                              |
| **new_entry_data**     | BLOB      | **nullable**                              |

### **Relationships**
- Belongs to **User** → `user_id`

### Column Descriptions
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**user_id:** The user that the SecureData is associated with
**entry_name:** Name for the password entry. Encrypted with master_key, and stored with nonce and auth_tag
**entry_data:** Data for the password entry. Encrypted with master_key, and stored with nonce and auth_tag
**new_entry_name:** Temporary store for new encrypted password name, while changing password
**new_entry_data:** Temporary store for new encrypted password data, while changing password
