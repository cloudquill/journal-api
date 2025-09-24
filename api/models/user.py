from uuid import uuid4
from typing import Optional, Annotated
from pydantic import BaseModel, Field


class User(BaseModel):
    id: Annotated[str, Field(
        default_factory=lambda: str(uuid4())
    )]
    username: str
    disabled: Annotated[bool, Field(
        default=False
    )]


class UserInDB(User):
    hashed_password: str


class CreateUser(BaseModel):
    username: Annotated[str, Field(
        ...,
        min_length=2,
        max_length=25,
        description="The user's username"
    )]
    password: Annotated[str, Field(
        ...,
        min_length=2,
        description="The user's password"
    )]