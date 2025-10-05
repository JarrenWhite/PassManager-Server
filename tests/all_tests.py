import pytest
import os
import sys

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    exit_code = pytest.main(["-v", "-s", test_dir])
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
