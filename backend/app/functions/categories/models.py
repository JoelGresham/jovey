"""
Category Models
Pydantic models for category management
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class CategoryBase(BaseModel):
    """Base category fields"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True
    metadata: dict = Field(default_factory=dict)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is URL-friendly"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower()


class CategoryCreate(CategoryBase):
    """Model for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Model for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    metadata: Optional[dict] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Ensure slug is URL-friendly"""
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower() if v else v


class Category(CategoryBase):
    """Complete category model with database fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryWithChildren(Category):
    """Category with nested children"""
    children: list['CategoryWithChildren'] = Field(default_factory=list)
    product_count: int = 0


class CategoryTree(BaseModel):
    """Category hierarchy tree"""
    categories: list[CategoryWithChildren]
