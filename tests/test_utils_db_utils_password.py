import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.mock_classes import _MockSession, _MockQuery
from utils.db_utils_password import DBUtilsPassword
from database.database_models import User


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
            password_change=True
        )

        DBUtilsPassword.clean_password_change(
            db_session=mock_session,
            user=fake_user
        )

        assert fake_user.password_change == False


if __name__ == '__main__':
    pytest.main(['-v', __file__])
