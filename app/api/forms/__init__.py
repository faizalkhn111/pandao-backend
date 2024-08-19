from .blueprint import BluePrintTermsForm, BlurPrintForm
from pydantic import BaseModel, Field
from typing_extensions import Optional, List
from enum import Enum


## forms related to user start

class UserSignupForm(BaseModel):
    public_address: str = Field(..., description=" user Public address")
    username: str = Field(..., description=" user username")
    display_image: str = Field(..., description=" user display image")
    about: str = Field(..., description=" user about this user")
    image_url: Optional[str] = Field(None, description="User updated image URL")
    bio: Optional[str] = Field(None, description="User cover url")
    tags: list[str] = Field(None, description="community tags that user likes")


class UserLogin(BaseModel):
    public_address: str = Field(..., description="user wallet public address")


class UserProfileUpdate(BaseModel):
    about: Optional[str] = Field(None, description="User updated description")
    image_url: Optional[str] = Field(None, description="User updated image URL")
    public_address: str = Field(..., description="User wallet public address")
    website_url: Optional[str] = Field(None, description="User updated website URL")
    x_url: Optional[str] = Field(None, description="User updated X (Twitter) URL")
    linkedin: Optional[str] = Field(None, description="User updated LinkedIn URL")
    tiktok: Optional[str] = Field(None, description="User updated TikTok URL")
    cover_url: Optional[str] = Field(None, description="User cover url")
    bio: Optional[str] = Field(None, description="User cover url")
