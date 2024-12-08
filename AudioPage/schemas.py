from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TrackBase(BaseModel):
    title: str

class TrackCreate(TrackBase):
    author_id: int

class TrackDB(TrackBase):
    id: int
    artist: str
    author_id: int

    class Config:
        orm_mode = True


class TrackUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    path: Optional[str] = None

class Track(BaseModel):
    id: int
    title: str = Field(min_length=5, max_length=50)
    artist: str
    path: str

    @validator("path")
    def validate_path(cls, v):
        allowed_extensions = [".mp3", ".ogg", ".wav", "m4a"]
        ext = v[-4:]
        if ext not in allowed_extensions:
            raise ValueError("Unsupported extension")
        return v

class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    tracks: List[TrackDB] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    playlists: List["PlaylistDB"] = []

    class Config:
        orm_mode = True

class PlaylistBase(BaseModel):
    name: str

class PlaylistCreate(PlaylistBase):
    owner_id: int

class PlaylistDB(PlaylistBase):
    id: int
    owner_id: int
    tracks: List[TrackDB] = []

    class Config:
        orm_mode = True
