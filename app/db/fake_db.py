import bcrypt

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