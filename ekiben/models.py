from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, field_validator


SIZE_VALUES = {"1x1", "1x2", "2x1", "2x2"}


class Profile(BaseModel):
    name: str
    avatar: Optional[str] = None
    bio: Optional[str] = None


class Theme(BaseModel):
    background: str = "#f5f5f0"
    card_background: str = "#ffffff"
    accent: str = "#3b82f6"
    font_family: str = "system-ui, sans-serif"
    border_radius: int = 16
    card_shadow: bool = True


class LinkBlock(BaseModel):
    type: Literal["link"]
    size: str = "1x1"
    color: Optional[str] = None
    title: str
    url: str
    image: Optional[str] = None

    @field_validator("size")
    @classmethod
    def valid_size(cls, v: str) -> str:
        if v not in SIZE_VALUES:
            raise ValueError(f"size must be one of {SIZE_VALUES}")
        return v


class TextBlock(BaseModel):
    type: Literal["text"]
    size: str = "1x1"
    color: Optional[str] = None
    content: str

    @field_validator("size")
    @classmethod
    def valid_size(cls, v: str) -> str:
        if v not in SIZE_VALUES:
            raise ValueError(f"size must be one of {SIZE_VALUES}")
        return v


class SocialBlock(BaseModel):
    type: Literal["social"]
    size: str = "1x1"
    color: Optional[str] = None
    platform: Literal["x", "github", "misskey"]
    username: str
    instance: Optional[str] = None  # misskey only

    @field_validator("size")
    @classmethod
    def valid_size(cls, v: str) -> str:
        if v not in SIZE_VALUES:
            raise ValueError(f"size must be one of {SIZE_VALUES}")
        return v


class SpacerBlock(BaseModel):
    type: Literal["spacer"]
    size: str = "1x1"

    @field_validator("size")
    @classmethod
    def valid_size(cls, v: str) -> str:
        if v not in SIZE_VALUES:
            raise ValueError(f"size must be one of {SIZE_VALUES}")
        return v


Block = LinkBlock | TextBlock | SocialBlock | SpacerBlock


class SiteConfig(BaseModel):
    profile: Profile
    theme: Theme = Theme()
    blocks: list[Block] = []
