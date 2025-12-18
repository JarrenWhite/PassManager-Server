import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from services.service_user import ServiceUser



if __name__ == '__main__':
    pytest.main(['-v', __file__])
