import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_user import user_bp


class TestApiUser():
    """Test cases for the User API endpoints"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        yield


if __name__ == '__main__':
    pytest.main(['-v', __file__])
