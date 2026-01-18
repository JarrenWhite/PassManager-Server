import sys
import pytest
from pathlib import Path


def main():
    test_dir = Path(__file__).parent
    test_files = [str(f) for f in test_dir.glob("test_*.py")]

    if not test_files:
        print("No test files found.")
        sys.exit(1)

    exit_code = pytest.main(test_files)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
