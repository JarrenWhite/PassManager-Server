import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

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
        clear_mappers()
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



if __name__ == '__main__':
    pytest.main(['-v', __file__])
