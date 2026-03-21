import os
import sys
import pytest
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.user_handler import UserHandler


class TestRegister:
    """Test cases for user register function"""


if __name__ == '__main__':
    pytest.main(['-v', __file__])
