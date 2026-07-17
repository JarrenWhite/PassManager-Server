from datetime import datetime
from typing import Tuple, Optional

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.orm import Session

from database import DatabaseSetup, User, AuthEphemeral, LoginSession
from enums import FailureReason
from .db_utils_password import DBUtilsPassword


class DBUtilsAuth():
    """Utility functions for managing auth based database functions"""

    @staticmethod
    def _check_expiry(
        db_session: Session,
        auth_ephemeral: AuthEphemeral
    ) -> bool:
        """
        Checks if an auth ephemeral is expired, and cleans up appropriately

        Returns:
            (bool)  True if expired & being deleted, false otherwise
        """
        is_expired = False

        if (
            auth_ephemeral.expiry_time and
            auth_ephemeral.expiry_time < datetime.now()
        ):
            is_expired = True

        if is_expired:
            logger.debug("Auth Ephemeral: %s has expired.", auth_ephemeral.public_id[-4:])
            if auth_ephemeral.password_change:
                logger.debug("Password Auth Ephemeral being passed for cleaning.")
                DBUtilsPassword.clean_password_change(
                    db_session=db_session,
                    user=auth_ephemeral.user
                )
            else:
                db_session.delete(auth_ephemeral)

        return is_expired


    @staticmethod
    def fetch(
        username_hash: Optional[bytes] = None,
        user_id: Optional[int] = None
    ) -> Tuple[bool, Optional[FailureReason], int, bytes, bytes]:
        """
        Fetch the details required to begin an authorisation process

        Returns:
            (int)   user_id
            (bytes) srp_salt
            (bytes) srp_verifier
        """
        if username_hash is None and user_id is None:
            logger.error("Fetch called without arguments")
            return False, FailureReason.SERVER_ERROR, 0, b'', b''

        try:
            with DatabaseSetup.get_db_session() as session:
                query = session.query(User)
                if user_id is not None:
                    query = query.filter(User.id == user_id)
                else:
                    query = query.filter(User.username_hash == username_hash)

                user = query.first()

                if user is None:
                    identifier = username_hash[-4:] if username_hash is not None else user_id
                    logger.debug("User: %s not found.", identifier)
                    return False, FailureReason.NOT_FOUND, 0, b'', b''

                return True, None, user.id, user.srp_salt, user.srp_verifier
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, 0, b'', b''
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, 0, b'', b''


    @staticmethod
    def start(
        user_id: int,
        eph_private_b: bytes,
        eph_public_b: bytes,
        expiry_time: datetime
    ) -> Tuple[bool, Optional[FailureReason], str, bytes]:
        """
        Begin auth ephemeral session for the user

        Returns:
            (str)   public_id
            (bytes) master_key_salt
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if user is None:
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND, "", b''

                auth_ephemeral = AuthEphemeral(
                    user=user,
                    eph_private_b=eph_private_b,
                    eph_public_b=eph_public_b,
                    expiry_time=expiry_time,
                    password_change=False
                )
                session.add(auth_ephemeral)
                session.flush()

                logger.info("Auth Ephemeral: %s created.", auth_ephemeral.public_id[-4:])
                return True, None, auth_ephemeral.public_id, user.master_key_salt
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, "", b''
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, "", b''


    @staticmethod
    def get_details(
        username_hash: bytes,
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], bytes, bytes, bytes]:
        """
        Get the ephemeral details for the given ephemeral id

        Returns:
            (bytes) eph_private_b
            (bytes) eph_public_b
            (bytes) srp_verifier
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    logger.debug("Auth Ephemeral: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, b'', b'', b''
                if auth_ephemeral.user.username_hash != username_hash:
                    logger.debug("Auth Ephemeral: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, b'', b'', b''
                if DBUtilsAuth._check_expiry(session, auth_ephemeral):
                    logger.debug("Auth Ephemeral: %s expired.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, b'', b'', b''

                return (True, None,
                    auth_ephemeral.eph_private_b,
                    auth_ephemeral.eph_public_b,
                    auth_ephemeral.user.srp_verifier
                )
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, b'', b'', b''
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, b'', b'', b''


    @staticmethod
    def complete(
        public_id: str,
        session_key: bytes,
        maximum_requests: Optional[int],
        expiry_time: Optional[datetime]
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Complete login session creation

        Returns:
            (str)   public_id
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    logger.debug("Auth Ephemeral: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, ""
                if DBUtilsAuth._check_expiry(session, auth_ephemeral):
                    logger.debug("Auth Ephemeral: %s expired.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, ""
                if auth_ephemeral.password_change:
                    logger.debug("Auth Ephemeral: %s is password change type.", public_id[-4:])
                    return False, FailureReason.PASSWORD_CHANGE, ""

                login_session = LoginSession(
                    user=auth_ephemeral.user,
                    session_key=session_key,
                    request_count=0,
                    last_used=datetime.now(),
                    maximum_requests=maximum_requests,
                    expiry_time=expiry_time,
                    password_change=False
                )
                session.add(login_session)
                session.flush()
                session.delete(auth_ephemeral)

                logger.info("Login Session: %s created.", login_session.public_id[-4:])
                return True, None, login_session.public_id
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def clean_all(
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Remove all expired Auth Ephemerals from the database"""
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemerals = session.query(AuthEphemeral)
                for auth_ephemeral in auth_ephemerals:
                    _ = DBUtilsAuth._check_expiry(session, auth_ephemeral)

                logger.info("Auth Ephemerals cleaned.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION
