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

    def test_all_fields_correct(self):
        """Should store all fields correctly"""
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

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].username_hash == "fake_hash"
        assert users[0].srp_salt == "fake_srp_salt"
        assert users[0].srp_verifier == "fake_srp_verifier"
        assert users[0].master_key_salt == "fake_master_key_salt"
        assert users[0].new_srp_salt == "new_srp_salt"
        assert users[0].new_srp_verifier == "new_srp_verifier"
        assert users[0].new_master_key_salt == "new_master_key_salt"

    def test_can_edit_data(self):
        """Should be possible to adjust all fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].username_hash == "fake_hash"

        user.username_hash="new_fake_hash"
        user.srp_salt="new_fake_srp_salt"
        user.srp_verifier="new_fake_srp_verifier"
        user.master_key_salt="new_fake_master_key_salt"
        self.session.commit()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 0

        users = self.session.query(User).filter_by(username_hash="new_fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].username_hash == "new_fake_hash"
        assert users[0].srp_salt == "new_fake_srp_salt"
        assert users[0].srp_verifier == "new_fake_srp_verifier"
        assert users[0].master_key_salt == "new_fake_master_key_salt"

    def test_can_add_optional_fields_late(self):
        """Should be able to add optional fields at a later point"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user.new_srp_salt="new_srp_salt"
        user.new_srp_verifier="new_srp_verifier"
        user.new_master_key_salt="new_master_key_salt"
        self.session.commit()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].new_srp_salt == "new_srp_salt"
        assert users[0].new_srp_verifier == "new_srp_verifier"
        assert users[0].new_master_key_salt == "new_master_key_salt"

    def test_cannot_delete_required_fields(self):
        """Should not be possible to delete required fields"""
        user = User(
            username_hash="fake_hash",
            srp_salt="fake_srp_salt",
            srp_verifier="fake_srp_verifier",
            master_key_salt="fake_master_key_salt"
        )
        self.session.add(user)
        self.session.commit()

        user.username_hash=None
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.srp_salt=None
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.srp_verifier=None
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        user.master_key_salt=None
        try:
            self.session.commit()
            raise AssertionError("Expected not null constraint violation but no exception was raised")
        except Exception as e:
            error_message = str(e).lower()
            assert ("not null constraint failed" in error_message or "integrity" in error_message), f"Expected not null constraint violation, got: {error_message}"
            self.session.rollback()

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].username_hash == "fake_hash"
        assert users[0].srp_salt == "fake_srp_salt"
        assert users[0].srp_verifier == "fake_srp_verifier"
        assert users[0].master_key_salt == "fake_master_key_salt"

    def test_can_delete_completed_optional_fields(self):
        """Should be possible to delete optional fields"""
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

        users = self.session.query(User).filter_by(username_hash="fake_hash").all()
        assert len(users) == 1
        assert users[0].id == user.id


if __name__ == '__main__':
    pytest.main(['-v', __file__])
