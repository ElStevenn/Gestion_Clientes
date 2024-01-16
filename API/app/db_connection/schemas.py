from pydantic import BaseModel
from typing import Optional

class BaseUser(BaseModel):
    username: str
    email: str

class CreateUser(BaseUser):
    password: str # When it comes to create a new user, the application has to encrypt the password
    role_: Optional[str] = None


class UserModifyAtributes(BaseUser):
    role_: Optional[str] = None
