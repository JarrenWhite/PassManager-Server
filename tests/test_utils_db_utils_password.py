import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession
from utils.db_utils_password import DBUtilsPassword
from database.database_models import User, AuthEphemeral


class TestCleanPasswordChange():
    """Test cases for database utils password clean password change function"""

    def test_user_password_change_set_to_false(self):
        """Should change user password change status to false"""
        mock_session = _MockSession()

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            auth_ephemerals=[],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session,
            user=fake_user
        )

        assert fake_user.password_change == False

    def test_delete_auth_ephemeral(self):
        """Should delete any password change auth ephemerals"""
        mock_session = _MockSession()

        ephemeral = AuthEphemeral(
            user_id=1,
            public_id="valid_password_ephemeral",
            eph_private_b="fake_eph_private_b",
            eph_public_b="fake_eph_public_b",
            expiry_time=datetime.now() + timedelta(hours=1),
            password_change=True
        )

        fake_user = User(
            id=123456,
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            password_change=True,
            auth_ephemerals=[ephemeral],
            login_sessions=[],
            secure_data=[]
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session,
            user=fake_user
        )

        assert len(mock_session._deletes) == 1
        assert mock_session._deletes[0] == ephemeral


if __name__ == '__main__':
    pytest.main(['-v', __file__])
