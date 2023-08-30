from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(BaseModel):
    username: str
    email: str
