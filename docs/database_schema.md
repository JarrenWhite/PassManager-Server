# Database Schema

This document defines the database schema used within the password manager, as well as giving details about the various stored items.

## User

### Purpose
Store main user information, including SRP authentication data, salts for encryption, and references to user sessions and data.

### **Columns**

| Column              | Type      | Constraints                     |
|---------------------|-----------|---------------------------------|
| **id**              | BIGINT    | **Primary Key**, auto-increment |
| **username_hash**   | BLOB      | **Unique**, **Indexed**         |
| **srp_salt**        | BLOB      |                                 |
| **srp_verifier**    | BLOB      |                                 |
| **master_key_salt** | BLOB      |                                 |

### **Relationships**
- **LoginSessions** → `LoginSessions.user_id` (one-to-many) cascading delete
- **SecureData** → `SecureData.user_id` (one-to-many) cascading delete

### Column Descriptions
**id:** Database ID for the entry
**username:** Hash of the user's username
**srp_salt:** The salt used to create the verifier in SRP
**srp_verifier:** The verifier used to create secure session keys using SRP
**master_key_salt:** The salt used to create the master key
**login_session:** List of all linked LoginSession entries
**secure_data:** List of all linked SecureData entries

---


## LoginSession

### Purpose
Tracks user authentication sessions, storing session keys and related data.

### **Columns**

| Column              | Type      | Constraints / Notes                       |
|---------------------|-----------|-------------------------------------------|
| **id**              | BIGINT    | **Primary Key**, auto-increment           |
| **public_id**       | CHAR(36)  | **Unique**, **Indexed**                   |
| **user_id**         | BIGINT    | **Foreign Key** → `Users.id`, **Indexed** |
| **session_key**     | BLOB      |                                           |
| **request_count**   | INT       |                                           |
| **maximum_requests**| INT       | **nullable**                              |
| **expiry_time**     | TIMESTAMP | **nullable**                              |
| **last_used**       | TIMESTAMP |                                           |

### **Relationships**
- Belongs to **Users** → `user_id`

### Column Descriptions
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**user_id:** The user that the LoginSession is associated with
**session_key:** Key used for session encryption and safety. Encrypted with database_key, and stored with nonce and auth_tag
**request_count:** Number of successful requests made on this session so far
**maximum_requests:** Number of requests after which the session will expire
**expiry_time:** Time past which the session will expire
**last_used:** Time at which the session was last used

---


## SecureData

### Purpose
Stores encrypted password entries, and related nonce and auth_tag for decryption.

| Column                 | Type      | Constraints / Notes                       |
|------------------------|-----------|-------------------------------------------|
| **id**                 | BIGINT    | **Primary Key**, auto-increment           |
| **public_id**          | CHAR(36)  | **Unique**, **Indexed**                   |
| **user_id**            | BIGINT    | **Foreign Key** → `Users.id`, **Indexed** |
| **entry_name**         | BLOB      | **nullable**                              |
| **entry_data**         | BLOB      | **nullable**                              |

### **Relationships**
- Belongs to **Users** → `user_id`

### Column Descriptions
**id:** Database ID for the entry
**public_id:** Public ID for the entry (generated UUID)
**user_id:** The user that the SecureData is associated with
**entry_name:** Name for the password entry. Encrypted with master_key, and stored with nonce and auth_tag
**entry_data:** Data for the password entry. Encrypted with master_key, and stored with nonce and auth_tag
