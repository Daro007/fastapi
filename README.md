# FastAPI Backend

Welcome to the backend repository of the FastAPI project. This repository contains the code for the backend API built using FastAPI (Python). The backend provides user authentication, user management, and JWT-based authorization.

## Features

- User registration and login with JWT-based authentication.
- User profile management, including updating username and deleting account.
- Secure password hashing and verification.
- User data stored in a fake database (for demonstration purposes).

## Prerequisites

- Python 3.x
- Docker (for local development and deployment)

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/Daro007/fastapi.git
    ```

2. Build the project with Docker

    ```bash
   docker build -t fastapi .
    ```
3. Run the project with the following command

    ```bash
   docker run -d -p 8000:8000 fastapi
    ```

## API Documentation

The API documentation can be accessed at http://localhost:8000/docs or http://localhost:8000/redoc when the backend is running.