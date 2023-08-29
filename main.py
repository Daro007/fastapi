from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta
import secrets

secret_key = secrets.token_hex(32)
# print(secret_key)


# Configure CORS
origins = [
    "http://localhost:3000",  
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/healthcheck/')
async def healthcheck():
    return {"Hello": "World"}

# Fake DB
fake_users_db = {
    "testuser1": {
        "email": "testuser1@example.com",
        "username": "testuser1",
        "hashed_password": bcrypt.hashpw(b"testpassword1", bcrypt.gensalt()).decode('utf-8'),
    },
    "testuser2": {
        "email": "testuser2@example.com",
        "username": "testuser2",
        "hashed_password": bcrypt.hashpw(b"testpassword2", bcrypt.gensalt()).decode('utf-8'),
    },
}

# JWT configuration 
SECRET_KEY = secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
class PasswordHasher:
    def verify_password(self, plain_password, hashed_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

password_hasher = PasswordHasher()

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class UserInDB(BaseModel):
    username: str
    email: str

# User model
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# User creation and storage
def create_user(user, hashed_password):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    fake_users_db[user.username] = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password,
    }
    return user

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

# Route to get an access token
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = {"access_token": access_token, "token_type": "bearer", "username": user.username}
    # response = JSONResponse(content={"message": "Login successful"})
    # response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

# Route to create a new user
@app.post("/users/")
async def create_new_user(user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_in_db = UserInDB(username=user.username, email=user.email)
    created_user = create_user(user_in_db, hashed_password)
    return {"message": "User created successfully", "user_id": created_user.username}

# Route to get all users
@app.get("/users/", response_model=List[UserInDB])
async def get_all_users():
    users = [UserInDB(username=user_data["username"], email=user_data["email"]) for user_data in fake_users_db.values()]
    return users

# Route to modify username
@app.put("/users/{username}/modify-username/")
async def modify_username(username: str, new_username: str):
    user_data = fake_users_db.get(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update the user's username
    user_data["username"] = new_username
    fake_users_db[new_username] = user_data
    del fake_users_db[username]
    
    return {"message": "Username modified successfully", "new_username": new_username}

# Route to delete user
@app.delete("/users/{username}/delete/")
async def delete_user(username: str):
    if username in fake_users_db:
        del fake_users_db[username]
        return {"message": "User deleted successfully", "deleted_username": username}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
