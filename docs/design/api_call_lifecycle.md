# API Call Lifecycle

## Call Received
- Request received by RPC Method
- Pass Request to relevant service

## Service Handler
- If session locked, pass to SessionManager for unencrypted bytes
- Parse unencrypted bytes into protobuf message
- Pass protobuf fields to ServiceUtils for sanitising
- If required, make calls to SRPUtils
- Make calls to the relevant DBUtils
- If session encryption required, pass protobuf message to SessionManager for sealing
- If any errors have occurred, pass to ServiceUtils for error enumeration
- Pass response details back up to API for return

## SessionManager (Opening)
> Note: Not used if api request does not require session locking
- Sanitise session fields
- Fetch AES key & username from DBUtilsSession using 'get_details'
- Use AESUtils to decrypt the session encrypted data
- Return the decrypted session bytes to service handler

## SessionManager (Sealing)
> Note: Not used if api request does not require session locking
- Fetch AES key from DBUtilsSession using 'log_use' (to increment details)
- Use AESUtils to encrypt the session contents
- Populate a SessionResponse protobuf message with the encrypted data
- Return SessionResponse message to service handler
