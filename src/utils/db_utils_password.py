from datetime import datetime
from typing import Tuple, Optional, List

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.orm import Session

from enums import FailureReason
from database import DatabaseSetup, User, AuthEphemeral, SecureData, LoginSession


class DBUtilsPassword():
    """Utility functions for managing password change based database functions"""

    @staticmethod
    def clean_password_change(
        db_session: Session,
        user: User
    ):
        """Remove all partial password change entries, ephemerals and login sessions"""
        logger.info("Cleaned password change for User: %s.", user.username_hash[-4:])

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
        eph_private_b: bytes,
        eph_public_b: bytes,
        expiry_time: datetime,
        srp_salt: bytes,
        srp_verifier: bytes,
        master_key_salt: bytes
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
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND, ""
                if user.password_change:
                    logger.debug("User: %s undergoing password change.", user.username_hash[-4:])
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

                logger.info("Password Auth Ephemeral: %s created.", auth_ephemeral.public_id[-4:])
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
        session_key: bytes,
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
                    logger.debug("Auth Ephemeral: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, ""
                if auth_ephemeral.expiry_time < datetime.now():
                    if auth_ephemeral.password_change:
                        DBUtilsPassword.clean_password_change(session, auth_ephemeral.user)
                    else:
                        session.delete(auth_ephemeral)
                    logger.debug("Auth Ephemeral: %s expired.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, ""
                if auth_ephemeral.user.id != user_id:
                    logger.debug("Auth Ephemeral: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, ""
                if not auth_ephemeral.password_change:
                    logger.debug("Auth Ephemeral: %s not password change type.", public_id[-4:])
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

                logger.info("Password Login Session: %s created.", login_session.public_id[-4:])
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
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND, []
                if not user.new_srp_salt or not user.new_srp_verifier or not user.new_master_key_salt:
                    logger.debug("User: %s password change failed: Insufficient new srp details.", user.username_hash)
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
                        logger.debug("User: %s password change failed: Secure Data not all updated.", user.username_hash)
                        DBUtilsPassword.clean_password_change(session, user)
                        return False, FailureReason.INCOMPLETE, []

                    public_ids.append(secure_data.public_id)
                    secure_data.entry_name = secure_data.new_entry_name
                    secure_data.entry_data = secure_data.new_entry_data
                    secure_data.new_entry_name = None
                    secure_data.new_entry_data = None

                logger.info("Password change for User: %s completed.", user.username_hash[-4:])
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
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND

                DBUtilsPassword.clean_password_change(session, user)

                logger.info("Password change for User: %s cancelled.", user.username_hash[-4:])
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
        entry_name: bytes,
        entry_data: bytes
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Add new encrypted entries for a secure entry"""
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()

                if secure_data is None:
                    logger.debug("Secure Data: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.id != user_id:
                    logger.debug("Secure Data: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.new_entry_name or secure_data.new_entry_data:
                    logger.debug("Secure Data: %s has already been updated.", public_id[-4:])
                    DBUtilsPassword.clean_password_change(session, secure_data.user)
                    return False, FailureReason.DUPLICATE

                secure_data.new_entry_name = entry_name
                secure_data.new_entry_data = entry_data

                logger.info("Secure Data: %s updated for Password change.", public_id[-4:])
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION
