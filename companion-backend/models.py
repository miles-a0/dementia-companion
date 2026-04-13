from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str
    full_name: str = None

class UserResponse(UserBase):
    id: int
    full_name: str = None
    created_at: str = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class FamilyMemberBase(BaseModel):
    name: str
    relationship: str = None

class FamilyMemberCreate(FamilyMemberBase):
    photo_url: str = None

class FamilyMemberResponse(FamilyMemberBase):
    id: int
    photo_url: str = None

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    from_family_id: int
    text_content: str = None
    audio_url: str = None

class MessageResponse(BaseModel):
    id: int
    from_family_id: int
    text_content: str = None
    audio_url: str = None
    is_read: bool = False
    created_at: str = None

    class Config:
        from_attributes = True

class MusicFavoriteCreate(BaseModel):
    title: str
    artist: str = None
    audio_url: str = None
    cover_url: str = None

class MusicFavoriteResponse(MusicFavoriteCreate):
    id: int

    class Config:
        from_attributes = True

class PhotoAlbumCreate(BaseModel):
    name: str

class PhotoAlbumResponse(PhotoAlbumCreate):
    id: int

    class Config:
        from_attributes = True

class PhotoCreate(BaseModel):
    image_url: str
    caption: str = None

class PhotoResponse(PhotoCreate):
    id: int

    class Config:
        from_attributes = True