import logging
from typing import Annotated, Dict

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models.token import Token
from models.user import CreateUser
from services.auth_service import AuthService
from repositories.cosmos_repository import UserDB

router = APIRouter(prefix="/user/me")
logger = logging.getLogger("journal")

async def get_auth_service():
    async with UserDB() as db:
        yield AuthService(db)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/me/token")

@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    logger.info(f"Authenticating user: {form_data.username}")
    user = await auth_service.authenticate_user(
        form_data.username, 
        form_data.password
    )
    access_token = auth_service.create_access_token(
        data={"sub": user.id}
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register_user(
        user_data: CreateUser, 
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Dict[str, str]:
    logger.info(f"Registering user: {user_data.username}.")
    result = await auth_service.register_user(user_data.username, user_data.password)
    
    if result:
        return {"detail": f"User {user_data.username} registered successfully."}
    else:
        return {"detail": f"Username {user_data.username} is taken."}

@router.get("/")
async def read_users_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> str:
    user_id = await auth_service.get_current_user(token)
    return user_id