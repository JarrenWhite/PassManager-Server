import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_models import Base, User

class TestDatabaseUserModels():
    """Test cases for the User database model"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        yield

        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_can_create_user(self):
        """Should be able to create new user with minimal fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == "fake_hash"

    def test_can_use_optional_fields(self):
        """Should be able to create new user with optional fields"""

        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt",
            new_srp_salt="new_srp_salt",
            new_srp_verifier="new_srp_verifier",
            new_master_key_salt="new_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        db_user = self.session.query(User).first()
        assert db_user is not None
        assert db_user.username_hash == "fake_hash"

    def test_username_uniqueness(self):
        """Should enforce unique usernames"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user2 = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt_2",
            srp_verifier="fake_srp_verifier_2",
            master_key_salt="fake_master_key_salt_2"
        )
        self.session.add(user2)

        try:
            self.session.commit()
            raise AssertionError("Expected uniqueness constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("unique constraint failed" in error_message or "integrity" in error_message), f"Expected uniqueness constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id


if __name__ == '__main__':
    pytest.main(['-v', __file__])
