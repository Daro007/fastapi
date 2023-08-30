from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.routes import router as auth_router
from app.api.users.routes import router as users_router

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

app.include_router(users_router, tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])