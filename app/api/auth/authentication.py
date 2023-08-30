from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.utils.password import PasswordHasher
from app.db.fake_db import fake_users_db
from app.api.users.models import UserCreate, UserInDB
import secrets
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
password_hasher = PasswordHasher()

# User authentication
def authenticate_user(username, password):
    user_data = fake_users_db.get(username)
    if user_data and password_hasher.verify_password(password, user_data["hashed_password"]):
        return UserInDB(username=user_data["username"], email=user_data["email"])
    return None

# Create JWT token
def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt