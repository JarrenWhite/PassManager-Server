import os
import sys
import pytest
from flask import Flask
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.api_session import session_bp
from services.service_session import ServiceSession



if __name__ == '__main__':
    pytest.main(['-v', __file__])
