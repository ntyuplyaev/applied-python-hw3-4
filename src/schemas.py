from datetime import datetime
from pydantic import BaseModel, HttpUrl, validator, EmailStr, SecretStr
from typing import Optional
from typing import Union


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str or None = None
    expires_at: datetime or None = None

    @validator('expires_at')
    def set_expires_at(cls, value):
        if value and value.replace(tzinfo=None) < datetime.utcnow():
            raise ValueError("Expiration date must be in the future")
        return value


class LinkUpdate(BaseModel):
    new_url: HttpUrl


class LinkResponse(LinkCreate):
    short_url: str
    created_at: datetime


class LinkStats(BaseModel):
    original_url: HttpUrl
    created_at: str
    clicks: int
    last_accessed: Optional[str]
    expires_at: Optional[str]


class ArchivedLinkStats(LinkStats):
    archived_at: datetime


class ProjectCreate(BaseModel):
    name: str


class ProjectResponse(ProjectCreate):
    id: int
    created_at: datetime


class ProjectWithLinks(ProjectResponse):
    links: list[LinkResponse]
