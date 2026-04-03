import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))


class TestCreate:
    """Test cases for data create function"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, monkeypatch):
        yield


if __name__ == '__main__':
    pytest.main(['-v', __file__])
