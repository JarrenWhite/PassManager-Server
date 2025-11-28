from datetime import datetime
from typing import Tuple, Optional, List

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.orm import Session

from database import DatabaseSetup, User, AuthEphemeral, SecureData, LoginSession
from .utils_enums import FailureReason


class DBUtilsPassword():
    """Utility functions for managing password change based database functions"""

    @staticmethod
    def clean_password_change(
        db_session: Session,
        user: User
    ):
        """Remove all partial password change entries, ephemerals and login sessions"""
        logger.info(f"Cleaned password change for User {user.username_hash[-4:]}.")

        user.password_change = False
        user.new_srp_salt = None
        user.new_srp_verifier = None
        user.new_master_key_salt = None

        for ephemeral in user.auth_ephemerals:
            if ephemeral.password_change:
                db_session.delete(ephemeral)

        for login_session in user.login_sessions:
            if login_session.password_change:
                db_session.delete(login_session)

        for secure_data in user.secure_data:
            secure_data.new_entry_name = None
            secure_data.new_entry_data = None


    @staticmethod
    def start(
        user_id: int,
        eph_private_b: str,
        eph_public_b: str,
        expiry_time: datetime,
        srp_salt: str,
        srp_verifier: str,
        master_key_salt: str
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Begin password auth ephemeral session for the user

        Returns:
            (str)   public_id
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if user is None:
                    logger.debug(f"User id: {user_id} not found.")
                    return False, FailureReason.NOT_FOUND, ""
                if user.password_change:
                    logger.debug(f"User {user.username_hash[-4:]} undergoing password change.")
                    return False, FailureReason.PASSWORD_CHANGE, ""

                user.password_change = True
                user.new_srp_salt = srp_salt
                user.new_srp_verifier = srp_verifier
                user.new_master_key_salt = master_key_salt

                auth_ephemeral = AuthEphemeral(
                    user=user,
                    eph_private_b=eph_private_b,
                    eph_public_b=eph_public_b,
                    expiry_time=expiry_time,
                    password_change=True
                )
                session.add(auth_ephemeral)
                session.flush()

                logger.info(f"Password Auth Ephemeral {auth_ephemeral.public_id[-4:]} created.")
                return True, None, auth_ephemeral.public_id
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def complete(
        user_id: int,
        public_id: str,
        session_key: str,
        expiry: datetime
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Complete password change login session creation

        Returns:
            (str)   public_id
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    logger.debug(f"Auth Ephemeral {public_id[-4:]} not found.")
                    return False, FailureReason.NOT_FOUND, ""
                if auth_ephemeral.expiry_time < datetime.now():
                    if auth_ephemeral.password_change:
                        DBUtilsPassword.clean_password_change(session, auth_ephemeral.user)
                    else:
                        session.delete(auth_ephemeral)
                    logger.debug(f"Auth Ephemeral {public_id[-4:]} expired.")
                    return False, FailureReason.NOT_FOUND, ""
                if auth_ephemeral.user.id != user_id:
                    logger.debug(f"Auth Ephemeral {public_id[-4:]} does not belong to user.")
                    return False, FailureReason.NOT_FOUND, ""
                if not auth_ephemeral.password_change:
                    logger.debug(f"Auth Ephemeral {public_id[-4:]} not password change type.")
                    return False, FailureReason.INCOMPLETE, ""

                secure_data_count = len(auth_ephemeral.user.secure_data)
                max_requests = (secure_data_count * 2) + 1

                login_session = LoginSession(
                    user=auth_ephemeral.user,
                    session_key=session_key,
                    request_count=0,
                    last_used=datetime.now(),
                    maximum_requests=max_requests,
                    expiry_time=expiry,
                    password_change=True
                )
                session.add(login_session)
                session.flush()
                session.delete(auth_ephemeral)

                logger.info(f"Password Login Session {login_session.public_id[-4:]} created.")
                return True, None, login_session.public_id
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def commit(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason], Optional[List[str]]]:
        """
        Complete password change process

        Returns:
            ([str]) [public_id]
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if user is None:
                    logger.debug(f"User id: {user_id} not found.")
                    return False, FailureReason.NOT_FOUND, []
                if not user.new_srp_salt or not user.new_srp_verifier or not user.new_master_key_salt:
                    logger.debug(f"User {user.username_hash} password change failed: Insufficient new srp details.")
                    DBUtilsPassword.clean_password_change(session, user)
                    return False, FailureReason.INCOMPLETE, []

                user.password_change = False
                user.srp_salt = user.new_srp_salt
                user.srp_verifier = user.new_srp_verifier
                user.master_key_salt = user.new_master_key_salt
                user.new_srp_salt = None
                user.new_srp_verifier = None
                user.new_master_key_salt = None

                for login_session in user.login_sessions:
                    session.delete(login_session)

                public_ids = []

                for secure_data in user.secure_data:
                    if not secure_data.new_entry_name or not secure_data.new_entry_data:
                        logger.debug(f"User {user.username_hash} password change failed: Secure Data not all updated.")
                        DBUtilsPassword.clean_password_change(session, user)
                        return False, FailureReason.INCOMPLETE, []

                    public_ids.append(secure_data.public_id)
                    secure_data.entry_name = secure_data.new_entry_name
                    secure_data.entry_data = secure_data.new_entry_data
                    secure_data.new_entry_name = None
                    secure_data.new_entry_data = None

                logger.info(f"Password change for User {user.username_hash[-4:]} completed.")
                return True, None, public_ids
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, []
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, []


    @staticmethod
    def abort(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Abort the password change for a user"""
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if user is None:
                    logger.debug(f"User id: {user_id} not found.")
                    return False, FailureReason.NOT_FOUND

                DBUtilsPassword.clean_password_change(session, user)

                logger.info(f"Password change for User {user.username_hash[-4:]} cancelled.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def update(
        user_id: int,
        public_id: str,
        entry_name: str,
        entry_data: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Add new encrypted entries for a secure entry"""
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()

                if secure_data is None:
                    logger.debug(f"Secure Data {public_id[-4:]} not found.")
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.id != user_id:
                    logger.debug(f"Secure Data {public_id[-4:]} does not belong to user.")
                    return False, FailureReason.NOT_FOUND
                if secure_data.new_entry_name or secure_data.new_entry_data:
                    logger.debug(f"Secure Data {public_id[-4:]} has already been updated.")
                    DBUtilsPassword.clean_password_change(session, secure_data.user)
                    return False, FailureReason.DUPLICATE

                secure_data.new_entry_name = entry_name
                secure_data.new_entry_data = entry_data

                logger.info(f"Secure Data {public_id[-4:]} updated for Password change.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION
