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
        "username": "testuser1",
        "password": "testpassword1",
    },
    "testuser2": {
        "username": "testuser2",
        "password": "testpassword2",
    }
}

class User(BaseModel):
    username: str

class UserInDB(User):
    password: str

class UserCreate(User):
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

# Route to get a token for authentication
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if not authenticate_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": username, "token_type": "bearer"}

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
   
# Create a new user
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    fake_users_db[user.username] = {"username": user.username, "password": user.password}
    return user

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
