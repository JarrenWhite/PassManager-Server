import os
import sys
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))



if __name__ == '__main__':
    pytest.main(['-v', __file__])
