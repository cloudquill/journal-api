import os
import re
import logging
from datetime import datetime, timedelta

import jwt
import bcrypt

from models.user import UserInDB
from repositories.cosmos_repository import UserDB
from exceptions import IncorrectCredentials, UserAlreadyExists, WeakPassword

logger = logging.getLogger("journal")

SALT_ROUNDS = 10
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES"))
if not (SECRET_KEY and ALGORITHM and TOKEN_EXPIRE_MINUTES):
    logger.critical("Environment variables not loaded.")
    raise ValueError("Environment variables not loaded.")


class AuthService():
    def __init__(self, db: UserDB):
        self.db = db
        logger.debug("Initialized authentication service")
    
    async def get_user(self, username: str) -> UserInDB | None:
        user = await self.db.get_user(username)
        
        if len(user) != 0:
            logger.info("Retrieved user: %s", username)
            return UserInDB(**user[0])
        else:
            logger.error("User %s does not exist.", username)
            return None
    
    def check_password_strength(self, plain_password: str):
        if(
            len(plain_password) > 8 
            and re.search(r'[a-z]', plain_password) 
            and re.search(r'[A-Z]', plain_password) 
            and re.search(r'[0-9]', plain_password) 
            and re.search(r'[^A-Za-z0-9]', plain_password)
        ):
            return True
        else:
            logger.error("Could not register user: Password is weak.")
            raise WeakPassword(
                "Weak password. Password must be more than 8 characters, contain at least "
                "one lowercase, uppercase letter, number and special character."
            )
    
    def hash_password(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt(SALT_ROUNDS))
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    async def register_user(self, username: str, password: str) -> bool:
        existing_user = await self.get_user(username)
    
        if existing_user is None:
            logger.debug("Username %s is available.", username)
            
            self.check_password_strength(password)
            hashed_password = self.hash_password(password)
            enriched_user = UserInDB(
                username= username,
                hashed_password= hashed_password
            )

            await self.db.register_user(enriched_user)
            logger.info("User %s was successfully registered.", username)
            return True
        else:
            logger.error("Username %s is taken.", username)
            raise UserAlreadyExists(f"Username {username} is not available.")

    async def authenticate_user(self, username: str, password: str) -> UserInDB:
        user = await self.get_user(username)
        if not (user and self.verify_password(password, user.hashed_password)):
            logger.error("Incorrect username or password")
            raise IncorrectCredentials("Incorrect username or password")
        logger.info("User %s has logged in successfully.", username)
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug("Token issued successfully.")
        return encoded_jwt

    async def get_current_user(self, token: str) -> str:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub", None)
        if user_id is None:
            logger.error("Incorrect username or password")
            raise IncorrectCredentials("Incorrect username or password")
        return user_id