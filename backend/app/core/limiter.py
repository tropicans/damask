import os
import sys
from slowapi import Limiter
from slowapi.util import get_remote_address

# Disable rate limiting by default during unit tests to prevent cross-test rate limit exhaustion
is_testing = os.getenv("TESTING", "false").lower() in ("true", "1", "yes") or "pytest" in sys.modules

limiter = Limiter(key_func=get_remote_address, enabled=not is_testing)
