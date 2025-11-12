# Password Change Process

## Create Password Change Session
1) Start password change
    - DBUtilsPassword.start
2) Complete the Auth to get the Session
    - DBUtilsAuth.get_details
    - DBUtilsPassword.complete

## Edit Secure Data entry
1) Get the details of a specific entry
    - DBUtilsData.get_entry
2) Add new details for the entry
    - DBUtilsPassword.update

## Complete Password Change
1) Complete password change
    - DBUtilsPassword.commit

## Abort Password Change
1) Abort password change
    - DBUtilsPassword.abort
