import secrets
from datetime import timedelta

secret_key = secrets.token_hex(32)

# JWT configuration
SECRET_KEY = secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
