"""
Product Models
Pydantic models for product management
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ProductBase(BaseModel):
    """Base product fields"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=100, description="Product SKU (Stock Keeping Unit) - Required")
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None

    # Pricing
    base_price: Decimal = Field(..., ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)

    # Inventory
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    is_in_stock: bool = True

    # Product details
    specifications: dict = Field(default_factory=dict)
    features: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)

    # SEO & Display
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    is_featured: bool = False
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)

    # Manufacturing details
    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    warranty_months: int = Field(default=12, ge=0)

    # Additional metadata
    metadata: dict = Field(default_factory=dict)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is URL-friendly"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower()

    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v: str) -> str:
        """Ensure SKU follows naming convention"""
        if not v:
            raise ValueError('SKU is required')

        # SKU should be uppercase with hyphens
        sku_upper = v.upper()

        # Check format: should have at least 3 parts separated by hyphens
        parts = sku_upper.split('-')
        if len(parts) < 3:
            raise ValueError(
                'SKU must follow format: CATEGORY-POWER-APPLICATION-MATERIAL-FLOW_RATE-PRESSURE '
                '(minimum 3 parts)'
            )

        # Only allow alphanumeric and hyphens
        if not sku_upper.replace('-', '').isalnum():
            raise ValueError('SKU must contain only letters, numbers, and hyphens')

        return sku_upper


class ProductCreate(ProductBase):
    """Model for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None

    base_price: Optional[Decimal] = Field(None, ge=0)
    sale_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)

    stock_quantity: Optional[int] = Field(None, ge=0)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    is_in_stock: Optional[bool] = None

    specifications: Optional[dict] = None
    features: Optional[List[str]] = None
    images: Optional[List[str]] = None

    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)

    manufacturer: Optional[str] = Field(None, max_length=100)
    model_number: Optional[str] = Field(None, max_length=100)
    warranty_months: Optional[int] = Field(None, ge=0)

    metadata: Optional[dict] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Ensure slug is URL-friendly"""
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only letters, numbers, hyphens, and underscores')
        return v.lower() if v else v


class Product(ProductBase):
    """Complete product model with database fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True


class ProductWithCategory(Product):
    """Product with category information"""
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    category_path: Optional[str] = None
