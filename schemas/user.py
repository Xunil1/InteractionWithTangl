from pydantic import BaseModel, EmailStr, Field


class UserAuth(BaseModel):
    username: str
    password: str = Field(..., min_length=8)


class UserInfo(BaseModel):
    username: EmailStr
    access_token: str
    expire: int
