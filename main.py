from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware


# Configure CORS
origins = [
    "http://localhost:3000",  #Frontend URL here
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

fake_users_db = {
    "testuser1": {
        "email": "testuser1@example.com",
        "username": "testuser1",
        "password": "testpassword1",
    },
    "testuser2": {
        "email": "testuser2@example.com",
        "username": "testuser2",
        "password": "testpassword2",
    }
}

class User(BaseModel):
    username: str
    email: str

class UserCreate(User):
    password: str

class UserInDB(User):
    password: str


# OAuth2 password bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to get user from the database
def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)

# Function to verify user credentials
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user is None or user.password != password:
        return False
    return True


# Route to get a token for authentication
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    identifier = form_data.username  # This can be either username or email
    password = form_data.password
    user = next((u for u in fake_users_db.values() if u['username'] == identifier or u['email'] == identifier), None)
    if user is None or user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": user["username"], "token_type": "bearer"}


# Dependency to get the current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = token  # In this simple example, the token is the username
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


# Protected route that requires authentication
@app.get("/secure-route/")
async def secure_route(current_user: User = Depends(get_current_user)):
    return {"message": "This is a secure route", "user": current_user}


# Get all users
@app.get("/users/", response_model=List[User])
async def get_users():
    return fake_users_db.values()

# Get user by username
@app.get("/users/{username}", response_model=User)
async def get_user_by_username(username: str):
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_dict = fake_users_db[username]
    return UserInDB(**user_dict)
   
# Create a user
@app.post("/users/")
async def create_user(user: UserCreate):
    existing_user = next((u for u in fake_users_db.values() if u['username'] == user.username or u['email'] == user.email), None)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    user_data = {"username": user.username, "email": user.email, "password": user.password}
    fake_users_db[user.username] = user_data
    return user_data

# Modify a user
@app.put("/users/{username}", response_model=User)
async def update_user(username: str, user: UserCreate):
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    fake_users_db[username] = {"username": user.username, "password": user.password}
    return user

# Delete a user
@app.delete("/users/{username}", response_model=User)
async def delete_user(username: str):
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    deleted_user = fake_users_db.pop(username)
    return deleted_user
