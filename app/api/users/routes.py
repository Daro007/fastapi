from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.auth.authentication import oauth2_scheme
from app.api.users.models import UserCreate, UserInDB
from app.db.fake_db import fake_users_db
from app.utils.password import PasswordHasher
import bcrypt

router = APIRouter()
password_hasher = PasswordHasher()

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

@router.post("/users/")
async def create_new_user(user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_in_db = UserInDB(username=user.username, email=user.email)
    created_user = create_user(user_in_db, hashed_password)
    return {"message": "User created successfully", "user_id": created_user.username}

@router.get("/users/", response_model=List[UserInDB])
async def get_all_users():
    users = [UserInDB(username=user_data["username"], email=user_data["email"]) for user_data in fake_users_db.values()]
    return users

@router.put("/users/{username}/modify-username/")
async def modify_username(username: str, new_username: str):
    user_data = fake_users_db.get(username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user_data["username"] = new_username
    fake_users_db[new_username] = user_data
    del fake_users_db[username]
    
    return {"message": "Username modified successfully", "new_username": new_username}

@router.delete("/users/{username}/delete/")
async def delete_user(username: str):
    if username in fake_users_db:
        del fake_users_db[username]
        return {"message": "User deleted successfully", "deleted_username": username}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )