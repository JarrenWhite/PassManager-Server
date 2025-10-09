# API Call Lifecycle

## Call Received
- Call received into the API receipt
- Parse data into JSON (If not already)
- Pass JSON into the SessionHandler

## SessionManager
- If call using session, pass to SessionManager to open
- Once session opened, (or if not session-locked), use ServiceUtils to sanitise inputs
- If required, make calls to SRPUtils
- Make calls to the relevant DBUtils
- If session encryption required, pass to SessionManager for sealing
- If any errors have occurred, pass to ServiceUtils for error enumeration
- Pass response details back up to API for return

## SessionManager (Opening)
> Note: Not used if api request does not require session locking
- Sanitise session details
- Fetch key & username from DBUtilsSession using 'get_details'
- Use AESUtils to decrypt the session
- Use EncodingParser to decode the data into json
- Return the json to the SessionHandler, along with the user id

## SessionManager (Sealing)
> Note: Not used if api request does not require session locking
- Use EncodingParser to encode the data into UTF8
- Fetch key from DBUtilsSession using 'log_use' (to increment details)
- Use AESUtils to encrypt the session contents
- Return details to
