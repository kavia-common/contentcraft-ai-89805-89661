from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BlogBase(BaseModel):
    title: str = Field(..., description="Blog title")
    prompt: Optional[str] = Field(default=None, description="Prompt used for generation")
    generated_content: Optional[str] = Field(default=None, description="Generated content")
    edited_content: Optional[str] = Field(default=None, description="Edited content")
    status: str = Field(default="draft", description="Blog status: draft, published, archived")


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(default=None, description="Blog title")
    edited_content: Optional[str] = Field(default=None, description="Edited content")
    status: Optional[str] = Field(default=None, description="Blog status")


class BlogOut(BlogBase):
    id: int = Field(..., description="Blog ID")
    author_id: int = Field(..., description="Author user id")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")


class BlogList(BaseModel):
    items: List[BlogOut]
    total: int
