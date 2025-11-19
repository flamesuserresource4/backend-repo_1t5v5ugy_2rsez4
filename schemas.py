"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# Album share app schemas

class Album(BaseModel):
    """
    Albums collection schema
    Collection name: "album"
    """
    title: str = Field(..., min_length=1, max_length=120, description="Album title")
    owner_name: Optional[str] = Field(None, max_length=80, description="Owner or creator display name")
    cover_url: Optional[HttpUrl] = Field(None, description="Optional cover image URL")
    slug: Optional[str] = Field(None, description="Shareable slug for the album")

class Photo(BaseModel):
    """
    Photos collection schema
    Collection name: "photo"
    """
    album_id: str = Field(..., description="Reference to album _id as string")
    url: HttpUrl = Field(..., description="Publicly accessible image URL")
    caption: Optional[str] = Field(None, max_length=200, description="Optional caption")
    added_by: Optional[str] = Field(None, max_length=80, description="Name of the contributor")

# Optional helper for returning an album with its photos
class AlbumWithPhotos(BaseModel):
    id: str
    title: str
    owner_name: Optional[str] = None
    cover_url: Optional[HttpUrl] = None
    slug: Optional[str] = None
    photos: List[dict] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
